# views.py
import redis
import json
from django.shortcuts import render, redirect

# Redis bağlantısı
r = redis.Redis(
    host='redis',      # docker-compose'daki servis adı
    port=6379,
    password='Aa25112002-redis',
    decode_responses=True  # string olarak döndürür
)

# Kullanıcıları listele
def users_list(request):
    users = []
    for key in r.keys("user:*"):
        users.append({
            "key": key,
            "data": json.loads(r.get(key))
        })
    return render(request, "users.html", {"users": users})

# Görevleri listele ve güncelle
def tasks_list(request):
    key = "config:lig:platin"  # örnek görev key
    tasks = json.loads(r.get(key))

    if request.method == "POST":
        # Formdan gelen değişiklikleri kaydet
        for i, task in enumerate(tasks):
            task_text = request.POST.get(f"text_{i}")
            task_status = request.POST.get(f"status_{i}")
            task["text"] = task_text
            task["status"] = task_status

        # Redis'e geri yaz
        r.set(key, json.dumps(tasks))
        return redirect("tasks_list")  # tekrar sayfayı yükle

    return render(request, "tasks.html", {"tasks": tasks})

def abi_talebe_wa_listesi(request):
    gruplar = {}

    for key in r.keys("user:*"):
        raw_data = r.get(key)
        if not raw_data:
            continue

        data = json.loads(raw_data)

        #talebe_id = key.decode().replace("user:", "")   # <<< KRİTİK
        talebe_id = key.replace("user:", "")

        abi = data.get("abi_adi", "Atanmamış")
        wa_id = data.get("platforms", {}).get("wa", "WA Bilgisi Yok")
        lig = data.get("lig", "Lig Belirsiz")
        isim = data.get("name", "İsimsiz")

        if abi not in gruplar:
            gruplar[abi] = []

        gruplar[abi].append({
            "id": talebe_id,      # <<< frontend için şart
            "wa_id": wa_id,
            "lig": lig,
            "isim": isim
        })

    return render(request, "wa_listesi.html", {"gruplar": gruplar})

# Dashboard
def dashboard(request):
    return render(request, "dashboard.html")

# Persons
def persons_list(request):
    return render(request, "persons/list.html")

def person_detail(request, pk):
    return render(request, "persons/detail.html")

def person_create(request):
    return render(request, "persons/create.html")

# Groups
def groups_list(request):
    return render(request, "groups/list.html")

def group_detail(request, pk):
    return render(request, "groups/detail.html")

def group_create(request):
    return render(request, "groups/create.html")

def group_edit(request, pk):
    return render(request, "groups/edit.html")

# Packages
def packages_list(request):
    return render(request, "packages/list.html")

def package_detail(request, pk):
    return render(request, "packages/detail.html")

def package_create(request):
    return render(request, "packages/create.html")

def package_edit(request, pk):
    return render(request, "packages/edit.html")
