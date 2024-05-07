import swan

while True:
    text  = input('swan > ')
    result,error=swan.run('<stdin>',text)
    
    if error: print(error.as_string())
    else: print(result)
    
#işlevi, girilen metni işleyerek bir sonuç üretir. Bu işlev, text adlı parametreyle birlikte çağrılır ve bir sonuç ve bir hata nesnesi (varsa) döndürür. 
# Eğer bir hata oluşursa, bu hata error adlı değişkene atanır, aksi takdirde sonuç result değişkenine atanır.
#Daha sonra, bir kontrol yapılır: Eğer bir hata varsa, print(error.as_string()) çağrısı ile hatayı kullanıcıya gösterilir. 
# Aksi halde, sonucu (result) doğrudan ekrana yazdırır.