import json
import jwt
import qrcode
import os
import requests
from io import BytesIO
from datetime import datetime
import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.conf import settings

from django.db.models import Sum, Count
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from .models import MenuItem, Order,AISuggestion


JWT_SECRET = getattr(settings, 'JWT_SECRET', 'mysecret')


# ─── Page Views ───────────────────────────────────────────────

def menu_page(request):
    return render(request, 'restaurant/menu.html')


def admin_page(request):
    return render(request, 'restaurant/admin.html')


# ─── JWT Helpers ──────────────────────────────────────────────

def generate_token(table_no):
    return jwt.encode({"table_no": str(table_no)}, JWT_SECRET, algorithm="HS256")


def decode_token(token):
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])


# ─── QR Code Generation ───────────────────────────────────────

@require_http_methods(["GET"])
def generate_qr(request):
    table_no = request.GET.get('table', '1')
    base_url = request.build_absolute_uri('/menu/')
    token = generate_token(table_no)
    url = f"{base_url}?token={token}"

    # QR via API (no Pillow needed)
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={url}"

    return JsonResponse({
        'token': token,
        'url': url,
        'qr_image': qr_url,
        'table': table_no
    })


# ─── Decode Token ─────────────────────────────────────────────

@require_http_methods(["GET"])
def decode_token_api(request):
    token = request.GET.get('token', '')
    try:
        data = decode_token(token)
        return JsonResponse({'status': 'success', 'table_no': data['table_no']})
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Invalid token'})


# ─── Menu CRUD ────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def menu_api(request):
    if request.method == 'GET':
        items = MenuItem.objects.all()
        return JsonResponse([i.to_dict() for i in items], safe=False)

    if request.method == 'POST':
        try:
            if request.content_type and 'multipart' in request.content_type:
                data = request.POST
                image = request.FILES.get('image')
            else:
                data = json.loads(request.body)
                image = None

            name = data.get('name', '').strip()
            if not name:
                return JsonResponse({'error': 'Name required'}, status=400)

            if MenuItem.objects.filter(name=name).exists():
                return JsonResponse({'message': 'Item already exists', 'error': True}, status=400)

            item = MenuItem.objects.create(
                name=name,
                price=int(data.get('price', 0)),
                category=data.get('category', ''),
                stock=int(data.get('stock', 0)),
                available=bool(int(data.get('available', 1))),
                image=image,
            )
            return JsonResponse({'message': 'Item added', 'item': item.to_dict()}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def menu_item_api(request, item_id):
    try:
        item = MenuItem.objects.get(id=item_id)
        item.delete()
        return JsonResponse({'message': 'Item deleted'})
    except MenuItem.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)


# ─── Orders ───────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def create_order(request):
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'error': 'Invalid request body'}, status=400)

    token = (body.get('token') or '').strip()
    if not token:
        return JsonResponse({'error': 'Missing table token. Please scan the table QR code again.'}, status=400)

    try:
        decoded = decode_token(token)
        table_no = decoded['table_no']
    except jwt.ExpiredSignatureError:
        return JsonResponse({'error': 'This QR code link has expired. Please scan the table QR code again.'}, status=400)
    except jwt.PyJWTError:
        # Covers DecodeError ("Invalid crypto padding" etc.), InvalidSignatureError, etc.
        return JsonResponse({'error': 'Invalid table QR code. Please scan the table QR code again.'}, status=400)

    try:
        items = body.get('items', [])
        if not items:
            return JsonResponse({'error': 'Cart is empty'}, status=400)
        total = body.get('total', sum(i['price'] * i['quantity'] for i in items))

        order = Order.objects.create(
            table_number=table_no,
            items=items,
            total=total,
            status='pending',
        )
        return JsonResponse({'message': 'Order placed successfully', 'table': table_no, 'order_id': order.id})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["GET"])
def get_orders(request):
    orders = Order.objects.all().order_by('-id')
    return JsonResponse([o.to_dict() for o in orders], safe=False)


@csrf_exempt
@require_http_methods(["PATCH"])
def update_order_status(request, order_id):
    try:
        body = json.loads(request.body)
        order = Order.objects.get(id=order_id)
        order.status = body.get('status', order.status)
        order.save()
        return JsonResponse({'message': 'Updated', 'order': order.to_dict()})
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)


def get_analytics(request):
    filter_type = request.GET.get("filter", "daily")  # daily / weekly / monthly

    if filter_type == "daily":
        trunc = TruncDay("created_at")
    elif filter_type == "weekly":
        trunc = TruncWeek("created_at")
    else:
        trunc = TruncMonth("created_at")

    sales = (
        Order.objects
        .annotate(period=trunc)
        .values("period")
        .annotate(
            total_sales=Sum("total"),
            order_count=Count("id")
        )
        .order_by("period")
    )

    # Top selling items
    item_counter = {}

    orders = Order.objects.all()
    for order in orders:
        for item in order.items:
            name = item["name"]
            qty = item["quantity"]
            item_counter[name] = item_counter.get(name, 0) + qty

    top_items = sorted(item_counter.items(), key=lambda x: x[1], reverse=True)[:5]

    return JsonResponse({
        "sales": list(sales),
        "top_items": top_items
    })




def ai_suggestions(request):
    latest = AISuggestion.objects.order_by("-created_at").first()

    return JsonResponse({
        "suggestions": latest.text if latest else "Insights not generated yet"
    })


def analytics_page(request):
    return render(request, "restaurant/analytics.html")