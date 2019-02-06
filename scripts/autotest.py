from Jumpscale import j

cl = j.clients.telegram_bot.get("test", bot_token_="626574765:AAGD5c949N3-za-CtUSba2aXQy-4ThhoD3s")
cl.send_message(chatid="@hamadatest", text="Hello from OVH")


