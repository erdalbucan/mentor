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
    key = "config:lig:altin"  # örnek görev key
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


from django.shortcuts import render

def dashboard(request):
    return render(request, "dashboard.html")


def persons_list(request):
    return render(request, "persons/list.html")


def person_detail(request, pk):
    return render(request, "persons/detail.html")


def groups_list(request):
    return render(request, "groups/list.html")


def group_detail(request, pk):
    return render(request, "groups/detail.html")


def packages_list(request):
    return render(request, "packages/list.html")

def package_detail(request, pk):
    return render(request, "packages/detail.html")

def person_create(request):
    return render(request, "persons/create.html")

def group_create(request):
    return render(request, "groups/create.html")

def group_edit(request, pk):
    return render(request, "groups/edit.html")

def package_create(request):
    return render(request, "packages/create.html")

def package_edit(request, pk):
    return render(request, "packages/edit.html")
