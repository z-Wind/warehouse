"""warehouse URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

# 1. 根據 `TEMPLATE_DIRS` 設定值，在指定的目錄中尋找名稱符合者。（這個設定的預設值是空 tuple，所以 Django 預設會跳過這個步驟。）
# 2. 在每個 app 中尋找 `templates` 目錄，並根據 `INSTALLED_APPS` 順序尋找名稱符合者。
# 所以不論你把這個檔案放在任一個 app 中，Django 都找得到。**如果同時有 `home.html`，Django 會優先使用第一個找到的版本**
# 為了避免 template 名稱與其他 apps 中的檔案衝突，通常會在 `templates` 目錄中使用子目錄，達到類似 namespacing 的效果。
# URL patterns 越來越多，`urls.py` 就會開始越長越大，因為 Django 是依照順序逐項比對 URL，
# 所以如果有太多路徑，後面的項目比對起來就會非常慢。
# 通常會把 URL 分類，只在最頂層（`lunch/urls.py`）留下最常用也最簡單的 patterns，降低 Django 比對時需要的運算量。
urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('goodsManage.urls')),
]