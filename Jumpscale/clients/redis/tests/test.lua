local processid = KEYS[1]
local cat = KEYS[2]
local message = KEYS[3]

local logkey = "queues:logs"



--local v = {}
--
--v["node"] = node
--v["message"] = message
--v["tags"] = tags
--v["level"] = level
--v["epoch"] = now
--
---- keep logs queue under 5000 line
--redis.call("RPUSH", logkey, cjson.encode(v))
--redis.call("LTRIM", logkey, -5000, -1)

return "OK "..processid..cat..message

