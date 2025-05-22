from rpi.resource import Resource

res = Resource()
try:
    while True:
        input('Enter to trigger ultra sonic sensor...')

        d = res.get_distance()
        if d < 0:
            raise ValueError('Get distance fail')

        print(f'distance: {d}')
except KeyboardInterrupt:
    pass