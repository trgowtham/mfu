### Files:

1. schemes.csv:
2. api_scrap.py: scrap URL randomly and catures scheme details if found. Scheme details found will be appeneded to schemes.csv. Input wil be 2 numbers, start and end of loop. Script will search for schemes between those 2 numbers.
 

### Run:

```console
# Nothing new found
 % python api_scrap.py 103600 103616                                                                                 (scrap-api)mfu
Iterating from 103600->103616
Found 12 schemes
Found 0 new schemes
```


```console
# New schemes found
 % python api_scrap.py 103600 103620                                                                                 (scrap-api)mfu
Iterating from 103600->103620
Found 16 schemes
Found 4 new schemes
```