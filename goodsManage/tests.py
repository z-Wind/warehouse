from django.test import TestCase
from django.core.urlresolvers import reverse
from .urls import urlpatterns

# Create your tests here.
#Python 會自動尋找 `TestCase` subclass 中以 `test` 開頭的 methods 並執行。
#`assert` 開頭的 method 是測試的重點，失敗的話整個測試就會被標注為 failed；`assertEqual` 是用來測試兩個引數是否相等。
class AllViewTests(TestCase):
    def test_all_view(self):
        for url in urlpatterns:    
            response = self.client.get(reverse(url.name))
            self.assertEqual(response.status_code, 200)
            # 測試是否使用 template
            # self.assertTemplateUsed(response, 'home.html')
        
