--[[



--]]
redis.replicate_commands()
local namespace = KEYS[1]
local key = KEYS[2]
local data = KEYS[3]

--
--local namespace = ARGV[1]
--local key = ARGV[2]
--local data = ARGV[3]

-- key for the id
local lastid_key = "bcdbstor:lastid"

local ns_key = "bcdbstor:"..namespace
local ns_lastid_key = ns_key..":lastid"
local ns_data_key = ns_key..":data"


local t = redis.call('TIME')[1]
local id = redis.call("INCR",lastid_key)

redis.breakpoint()

--
--if id>1000 then
--    redis.call("hdel", logkey, id-1000)
--end
--
--
--
--redis.call("HSET",logkey,id,data)
--
--redis.call("PUBLISH",channelkey,data_in)


return "OK "..id

