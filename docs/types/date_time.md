# date & time 

Base type is an epoch

## duration

duration e.g. 1w, 1d, 1h, 1m, 1

- w = week
- d = day
- h = hour
- m = minute

translates to seconds when used

## date

### epoch

is 4 bytes integer, can be retrieved using

```python
```

there are many more types see j.data.types

### <a name="date_supported_formats"></a> Date supported formats

- month/day  (will be current year if specified this way)
- year(4char)/month/day
- year(4char)/month/day
- year(2char)/month/day
- day/month/4char
- year(4char)/month/day

### <a name="date_time_supported_formats"></a> Date Time supported formats

- month/day 22:50
- month/day  (will be current year if specified this way)
- year(4char)/month/day
- year(4char)/month/day 10am:50
- year(2char)/month/day
- day/month/4char
- year(4char)/month/day 22:50
- +4h
- -4h