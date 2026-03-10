from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import easyocr
import re
import os

app = Flask(__name__)
app.secret_key = "dorala_secret_key"
CORS(app)

# 初始化 AI 辨識引擎
reader = easyocr.Reader(['ch_tra', 'en'])

# 收費邏輯設定
def calculate_fee(text, is_south, is_original):
    fee = 12.5  # 預設物品類
    category = "一般物品"
    
    # 自動辨識分類
    if any(x in text for x in ["卡", "券", "元", "商品卡", "禮券"]):
        fee = 10.5
        category = "禮物卡"
    elif any(x in text for x in ["正隆", "山隆", "衛生紙"]):
        fee = 15.0
        category = "衛生紙/超重"
    
    # 加價項
    if is_south: fee += 2
    if is_original: fee += 2
    
    return fee, category

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload():
    file = request.files['file']
    is_south = request.form.get('is_south') == 'true'
    is_original = request.form.get('is_original') == 'true'
    
    # 儲存圖片並辨識
    img_path = "temp.png"
    file.save(img_path)
    results = reader.readtext(img_path, detail=0)
    full_text = "".join(results)
    
    # 找公司代碼 (4位數)
    code_match = re.search(r'\d{4}', full_text)
    code = code_match.group() if code_match else "未知"
    
    fee, cat = calculate_fee(full_text, is_south, is_original)
    
    return jsonify({
        "code": code,
        "category": cat,
        "fee": fee,
        "raw_text": full_text[:20] + "..."
    })

if __name__ == '__main__':
    app.run(debug=True)
