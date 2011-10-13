from flaskext.wtf import (validators, HiddenField, SelectField,
    TextField, Form, TextAreaField, IntegerField)


RECORD_CHOICES = [
    ('A', 'A'),
    ('AAAA', 'AAAA'),
    ('CNAME', 'CNAME'),
    ('MX', 'MX'),
    ('NS', 'NS'),
    ('PTR', 'PTR'),
    ('SOA', 'SOA'),
    ('SPF', 'SPF'),
    ('SRV', 'SRV'),
    ('TXT', 'TXT'),
]

ALIAS_RECORD_CHOICES = [
    ('A', 'A'),
    ('AAAA', 'AAAA'),
    ('CNAME', 'CNAME'),
]


class PreviousHiddenField(HiddenField):
    def process(self, formdata, data=None):
        self.data = formdata.get(self.name,
            formdata.get(self.name.replace('previous_', '')))


class ZoneForm(Form):
    name = TextField('Domain Name', validators=[validators.Required()])
    comment = TextAreaField('Comment')


class RecordForm(Form):
    type = SelectField("Type", choices=RECORD_CHOICES)
    name = TextField("Name", validators=[validators.Required()])
    value = TextField("Value", validators=[validators.Required()])
    ttl = IntegerField("TTL", default="86400", validators=[validators.Required()])
    comment = TextAreaField("Comment")

    @property
    def values(self):
        if self.type.data != 'TXT':
            return filter(lambda x: x,
                      map(lambda x: x.strip(),
                          self.value.data.strip().split(';')))
        else:
            return [self.value.data.strip()]


class EditRecordForm(RecordForm):
    previous_type = PreviousHiddenField("Type",
        validators=[validators.Required()])

    previous_name = PreviousHiddenField("Name",
        validators=[validators.Required()])

    previous_value = PreviousHiddenField("Value",
        validators=[validators.Required()])

    previous_ttl = PreviousHiddenField("TTL",
        validators=[validators.Required()])

    @property
    def previous_values(self):
        if self.type.data != 'TXT':
            return filter(lambda x: x,
                      map(lambda x: x.strip(),
                          self.previous_value.data.strip().split(';')))
        else:
            return [self.previous_value.data.strip()]


class RecordAliasForm(Form):
    type = SelectField("Type", choices=ALIAS_RECORD_CHOICES)
    name = TextField("Name", validators=[validators.Required()])
    alias_hosted_zone_id = TextField("Alias Hosted Zone ID",
        validators=[validators.Required()])

    alias_dns_name = TextField("Alias DNS name", validators=[validators.Required()])

    ttl = IntegerField("TTL", default="86400",
            validators=[validators.Required()])

    comment = TextAreaField("Comment")

    @property
    def values(self):
        return None


class DeleteRecordAliasForm(RecordAliasForm):
    pass


class EditRecordAliasForm(RecordAliasForm):
    previous_type = PreviousHiddenField("Type",
        validators=[validators.Required()])

    previous_name = PreviousHiddenField("Name",
        validators=[validators.Required()])

    previous_alias_hosted_zone_id = PreviousHiddenField("Previous Alias Hosted Zone ID",
        validators=[validators.Required()])

    previous_alias_dns_name = PreviousHiddenField("Previous Alias DNS Name",
        validators=[validators.Required()])

    previous_ttl = PreviousHiddenField("TTL",
        validators=[validators.Required()])


class APIKeyForm(Form):
    key = TextField('API Key', validators=[validators.Required()])
