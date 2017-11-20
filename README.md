# CKStrReplace    

下載：[windows](https://github.com/xxi511/CKStrReplace/releases/download/0.0.1/CKStrReplace_windows.exe), [ubuntu](https://github.com/xxi511/CKStrReplace/releases/download/0.0.1/CKStrReplace_ubuntu)

這東西的作用基本上和[文字校正](https://github.com/xxi511/textCorrection/tree/python)類似，一樣是讀`data.txt`的資料          
差別在於它可以整本書去更改          
![](https://user-images.githubusercontent.com/10164640/33019746-9fde2f28-ce36-11e7-9bec-5b63b4dfcf13.png)       
* 帳密：CK的帳密      
* 網址：主題(小說)的網址     
* 頁數：要更改的範圍，沒防呆，輸入的時候自己注意一下          
都輸入好之後按下send開始，然後放著給它跑，跑完會跳通知         
如果出現沒有回應是正常的，不用理它         
如果有某樓的修正失敗，會紀錄在名為`failure.txt`，再去手動更改

`data.txt`跟之前有點不一樣新舊文字是以`->`來做區隔        
因為有的文字中間有空白          
如果是想刪除文字的話，新的文字請填`!@#$`          
```
舊的文字->新的文字
原因->事由
龍傲天->我
url->連結
那個人->被檢舉人
我是亂碼->!@#$
```
