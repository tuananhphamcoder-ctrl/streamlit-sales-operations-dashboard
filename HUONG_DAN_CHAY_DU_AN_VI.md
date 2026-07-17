# Hướng dẫn chạy dự án

## 1. Mở thư mục trong VS Code

Mở:

```text
streamlit-sales-operations-dashboard
```

## 2. Tạo môi trường

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.venv\Scripts\Activate.ps1
```

## 3. Cài thư viện

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 4. Chạy kiểm thử

```powershell
python -m pytest
```

## 5. Chạy dashboard

```powershell
python -m streamlit run app.py
```

## 6. Kiểm tra ba chế độ dữ liệu

- Use clean sample data
- Use messy sample data
- Upload my file

## 7. Deploy Streamlit

Repository: streamlit-sales-operations-dashboard
Branch: main
Main file path: app.py
