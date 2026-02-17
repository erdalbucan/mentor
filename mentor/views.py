# views.py

import redis
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse


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


def all_leagues_tasks(request):
    # 1. YENİ LİG OLUŞTURMA
    if request.method == "POST" and "new_league_name" in request.POST:
        new_name = request.POST.get("new_league_name").strip().lower()
        if new_name:
            new_key = f"config:lig:{new_name}"
            r.set(new_key, json.dumps([{"text": "İlk Görev"}]))
        return redirect("all_leagues_tasks")

    # 2. GÖREV İŞLEMLERİ (GÜNCELLE, EKLE, SİL)
    if request.method == "POST" and "league_key" in request.POST:
        target_key = request.POST.get("league_key")
        action = request.POST.get("action") # Formun ne yapacağını belirleyen input

        # Mevcut görevleri formdan topla
        updated_tasks = []
        for key_name, value in request.POST.items():
            if key_name.startswith(f"text_{target_key}_"):
                updated_tasks.append({"text": value})

        if action == "add_task":
            # Listeye yeni bir boş görev ekle
            updated_tasks.append({"text": "Yeni Görev"})

        elif action.startswith("delete_task_"):
            # Silinecek görevin index'ini al (örn: delete_task_3)
            idx = int(action.split("_")[-1])
            if 0 <= idx < len(updated_tasks):
                updated_tasks.pop(idx)

        # Redis'e güncel listeyi yaz
        r.set(target_key, json.dumps(updated_tasks))
        return redirect("all_leagues_tasks")
    # 3. VERİLERİ GETİRME
    leagues_data = {}
    keys = sorted(r.keys("config:lig:*")) # Ligleri alfabetik sıralar
    for key in keys:
        league_name = key.replace("config:lig:", "")
        raw_data = r.get(key)
        if raw_data:
            leagues_data[league_name] = {
                "key": key,
                "tasks": json.loads(raw_data)
            }
    return render(request, "all_tasks.html", {"leagues_data": leagues_data})

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
    # 1. Mevcut lig isimlerini Redis'ten çek
    ligler = [key.replace("config:lig:", "") for key in r.keys("config:lig:*")]
    
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

   #return render(request, "wa_listesi.html", {"gruplar": gruplar})
    return render(request, "wa_listesi.html", {
            "gruplar": gruplar, 
            "ligler": ligler
        })

# Lig güncelleme için yeni bir view fonksiyonu
def lig_guncelle(request):
    if request.method == "POST":
        data = json.loads(request.body)
        talebe_id = data.get("talebe_id")
        yeni_lig = data.get("yeni_lig")
        redis_key = f"user:{talebe_id}"
        user_data = json.loads(r.get(redis_key))
        user_data["lig"] = yeni_lig # Lig bilgisini güncelle

        r.set(redis_key, json.dumps(user_data))
        return JsonResponse({"status": "success"})

# Sürükle-bırak sonrası Redis'i güncelle
def talebe_tasi(request):
    if request.method == "POST":
        data = json.loads(request.body)
        talebe_id = data.get("talebe_id")
        yeni_abi = data.get("yeni_abi")
        redis_key = f"user:{talebe_id}"
        user_data = json.loads(r.get(redis_key))

        # Abi bilgisini güncelle (SET işlemi)
        user_data["abi_adi"] = yeni_abi
        r.set(redis_key, json.dumps(user_data))
        return JsonResponse({"status": "success"})

# Yeni kullanıcı (Talebe) oluşturma
def yeni_kullanici_ekle(request):
    if request.method == "POST":
        name = request.POST.get("name")
        wa_id = request.POST.get("wa_id")
        abi_adi = request.POST.get("abi_adi")
        lig = request.POST.get("lig")

        # Benzersiz bir ID oluştur (Örn: WA ID'nin sayısal kısmı)
        new_id = wa_id.split('@')[0] 
        redis_key = f"user:{new_id}"

        new_user = {
            "name": name,
            "role": "tlb",
            "lig": lig,
            "abi_adi": abi_adi,
            "platforms": {"wa": wa_id},
            "default_chat_id": new_id
        }

        r.set(redis_key, json.dumps(new_user))
        return redirect("abi_talebe_wa_listesi")

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
