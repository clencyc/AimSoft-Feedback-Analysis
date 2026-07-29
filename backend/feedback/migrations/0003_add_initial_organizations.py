from django.db import migrations


def create_organizations(apps, schema_editor):
    Organization = apps.get_model('feedback', 'Organization')
    names = ['Britam', 'Old mutual', 'CIC']
    for n in names:
        Organization.objects.get_or_create(name=n)


def remove_organizations(apps, schema_editor):
    Organization = apps.get_model('feedback', 'Organization')
    Organization.objects.filter(name__in=['Britam', 'Old mutual', 'CIC']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0002_add_feedbacklink_and_org'),
    ]

    operations = [
        migrations.RunPython(create_organizations, reverse_code=remove_organizations),
    ]
