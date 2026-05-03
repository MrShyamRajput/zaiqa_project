import os
import google.generativeai as genai
from .models import Order, AISuggestion

def generate_ai_suggestions():
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-2.5-flash")

        # 🔥 limit data (important for quota)
        orders = Order.objects.order_by("-id")[:30]

        context = [{"total": o.total, "items": o.items} for o in orders]

        prompt = f"""
        You are a restaurant growth expert.

        Analyze this order data:
        {context}

        Give:
        - 3 ways to increase sales
        - 2 upsell ideas
        - 2 low-performing item fixes

        Keep it short and practical.
        """

        response = model.generate_content(prompt)

        # ✅ only save if valid
        if response.text and len(response.text.strip()) > 20:
            AISuggestion.objects.create(text=response.text)

    except Exception as e:
        print("AI ERROR:", e)
        # ❌ don’t overwrite old data