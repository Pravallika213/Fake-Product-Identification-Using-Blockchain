from django.db import models
import json
import os

class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    quantity = models.IntegerField()
    fake = models.BooleanField(default=False)
    image = models.CharField(max_length=255 , default='None')
    photo = models.FileField(upload_to='photos/', default='None')

    def __str__(self):
        return self.name

    @property
    def photo_name(self):
        return os.path.basename(self.photo.name)

    def toJson(self):
        return json.dumps({'name': self.name,
                'price': self.price,
                'quantity': self.quantity,
                'fake': self.fake,
                'image': self.image}, default=lambda o: o.__dict__, sort_keys=True, indent=4)
