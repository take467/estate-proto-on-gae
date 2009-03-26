import datetime

class UtcTzinfo(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def dst(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return 'UTC'

    def olsen_name(self):
        return 'UTC'

class JstTzinfo(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(hours=9)

    def dst(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return 'JST'

    def olsen_name(self):
        return 'Asia/Tokyo'

def jst_date(value):
    if not value:
        value = datetime.datetime.now()

    value = value.replace(tzinfo=UtcTzinfo()). \
        astimezone(JstTzinfo())
    return value
