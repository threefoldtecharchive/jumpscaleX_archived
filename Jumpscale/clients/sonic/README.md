# Sonic server client
    
## usage example:

```python
    data = { 
         'post:1': "this is some test text hello", 
         'post:2': 'this is a hello world post', 
         'post:3': "hello how is it going?", 
         'post:4': "for the love of god?", 
         'post:5': "for the love lorde?", 
     } 
     client = j.clients.sonic.get('main', host="127.0.0.1", port=1491, password='dmdm') 
     for articleid, content in data.items(): 
         client.push("forum", "posts", articleid, content) 
     print(client.query("forum", "posts", "love")) 

    # ['post:5', 'post:4']

    print(client.suggest("forum", "posts", "lo"))                                
    # ['lorde', 'love']
```