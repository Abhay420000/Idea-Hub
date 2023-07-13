from django.db import models, IntegrityError
from django.contrib.auth.models import User
import random

class Articles(models.Model):
    pid = models.CharField(primary_key=True, max_length=10)
    title = models.CharField(max_length=75)
    body = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    updated = models.DateTimeField('updated on', auto_now=True)
    created = models.DateTimeField('created on', auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.pid:
            self.pid = self.get_ID()
        success = False
        failures = 0
        while not success:
            try:
                super(Articles, self).save(*args, **kwargs)
            except IntegrityError:
                 failures += 1
                 if failures > 5: # or some other arbitrary cutoff point at which things are clearly wrong
                     raise
                 else:
                     # looks like a collision, try another random value
                     self.pid = self.get_ID()
            else:
                 success = True
    
    def get_ID(self):
        #Generate ID
        l = [chr(x) for x in range(65,91)] + [chr(x) for x in range(97,123)] + [str(x) for x in range(0,10)]
        rcode = "".join(random.sample(l, 10))        
        return rcode 
    
    def __str__(self):
        ard = self.body[0:51].replace('\n', '')
        return f"{self.pid}.{self.title}: {ard}..."

class Comments(models.Model):
    cid = models.CharField(primary_key=True, max_length=15)
    comment = models.TextField()
    article = models.ForeignKey(Articles, related_name="comments", on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField('created on', auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.cid:
            self.cid = self.get_ID()
        success = False
        failures = 0
        while not success:
            try:
                super(Comments, self).save(*args, **kwargs)
            except IntegrityError:
                 failures += 1
                 if failures > 5: # or some other arbitrary cutoff point at which things are clearly wrong
                     raise
                 else:
                     # looks like a collision, try another random value
                     self.cid = self.get_ID()
            else:
                 success = True
    
    def get_ID(self):
        #Generate ID
        l = [chr(x) for x in range(65,91)] + [chr(x) for x in range(97,123)] + [str(x) for x in range(0,10)]
        rcode = "".join(random.sample(l, 15))        
        return rcode 
    
    def __str__(self):
        return f"{self.comment[0:25]}...  ON:{self.article.pid} BY:{self.owner.username}"

class Ratings(models.Model):
    like = models.BooleanField(default=False)
    dislike  = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Articles, on_delete=models.CASCADE)
    
    def __str__(self):
        if self.like:
            return f"{self.owner.username} liked {self.article.title[0:15]}"
        return f"{self.owner.username} disliked {self.article.title[0:15]}"