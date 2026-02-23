from langchain_community.llms import Ollama
from datetime import date,datetime
from RAG_APP.main import get_user_sales
from fastapi import APIRouter,Depends
from RAG_APP.main import check_current_user,get_db,sales
from sqlalchemy.orm import Session
from langchain.prompts import PromptTemplate
from datetime import date,datetime
model=Ollama(model="phi3:mini",temperature=0.0,base_url="http://localhost:11434",num_predict=500)
today_template="""
You are an AI assistant designed for small shopkeepers.

Your task is to generate “Today’s Sales Insight” using ONLY the provided sales data.

Data Context:
{sales_data}

Strict rules:
- Do NOT assume customer behavior.
- Do NOT compare with past days or trends.
- Do NOT invent data.
- Do NOT use time-based analysis.
- Use only product, quantity, price, and total.

Your response must be:
- Simple
- Honest
- Practical
- Easy to understand for non-technical users

Output structure (follow exactly):

📊 Today’s Sales Insight

🟢 Summary:
Briefly describe today’s sales in 2–3 simple lines based only on quantities and totals.

🔍 Observations:
List 2–3 clear observations derived strictly from quantity, price, and total.

💡 Advice for the Shopkeeper:
Give 2 practical suggestions.
Each suggestion must include a short explanation of why it is given.

⚠️ Note:
Provide one realistic caution or small improvement suggestion (if applicable).

Do not exaggerate.
Do not overpraise.
Focus on clarity and usefulness. """
router=APIRouter()
@router.get("/today_insight/")
async def get_today(user_id:int=Depends(check_current_user),db:Session=Depends(get_db)):
    today_date=date.today()
    data=get_user_sales(user_id=user_id,db=db)
    print(f"Sales data: {data}")
    
    if not data:
        return {
            "title":"Today's Insights",
            "insights":"No sales were recorded today."
        }
    
    # Format sales data for the prompt
    sales_text = "\n".join([
        f"- Product: {item.product_name}, Price: ₹{item.price}, Qty: {item.quantity}, Total: ₹{item.total}"
        for item in data
    ])
    
    template=PromptTemplate(
        template=today_template,
        input_variables=["sales_data"]
    )
    
    try:
        new_template=template.format(sales_data=sales_text)
        print(f"Formatted template: {new_template}")
        
        response=model.invoke(new_template)
        print(f"Model response: {response}")
        
        # Ensure response is a string
        insights_text = str(response).strip() if response else "Unable to generate insights"
        
        return {
            "title": "Today's Insights",
            "insights": insights_text,
            "success": True
        }
    except Exception as e:
        print(f"Error generating insights: {str(e)}")
        return {
            "title": "Today's Insights",
            "insights": f"Error: {str(e)}",
            "success": False
        }


