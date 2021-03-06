#!/usr/env/python
# models.py


import math
from PIL import Image
import numpy as np

from django.db import models
from django.contrib.auth.models import User



"""
Google Static Maps API URLs must be of the following form:

    http://maps.googleapis.com/maps/api/staticmap?parameters

see the docs at: https://developers.google.com/maps/documentation/staticmaps/
for more details.

Some other marker options::

    "&markers=color:green%7Clabel:A%7c{upleft_lat},{upleft_lon}"
    "&markers=color:green%7Clabel:B%7c{upright_lat},{upright_lon}"
    "&markers=color:green%7Clabel:C%7c{downright_lat},{downright_lon}"
    "&markers=color:green%7Clabel:D%7c{downleft_lat},{downleft_lon}"

"""
GOOGLE_STATIC_MAPS_URL_TEMPLATE ="\
http://maps.googleapis.com/maps/api/staticmap?\
size=500x500&maptype=hybrid&sensor=false\
&center={lastlat},{lastlon}\
&path=color:0x0000ff|weight:5|\
{upleft_lat},{upleft_lon}|\
{upright_lat},{upright_lon}|\
{downright_lat},{downright_lon}|\
{downleft_lat},{downleft_lon}|\
{upleft_lat},{upleft_lon}\
&markers=color:red%7Clabel:L%7c{lastlat},{lastlon}"

GOOGLE_STATIC_MAPS_URL_FIND_TEMPLATE = (GOOGLE_STATIC_MAPS_URL_TEMPLATE +
    "&markers=color:yellow%7Clabel:F%7c{findlat},{findlon}")

class Case(models.Model):
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    county = models.CharField(max_length=50)
    populationdensity = models.CharField(max_length=50)
    weather = models.CharField(max_length=50)

    lastlat = models.CharField(max_length=50)
    lastlon = models.CharField(max_length=50)
    findlat = models.CharField(max_length=50)
    findlon = models.CharField(max_length=50)

    case_name = models.CharField(max_length=50)
    Age = models.CharField(max_length=100)
    Sex = models.CharField(max_length=100)
    key = models.CharField(max_length=50)

    subject_category = models.CharField(max_length=50)
    subject_subcategory = models.CharField(max_length=50)
    subject_activity = models.CharField(max_length=50)


    scenario = models.CharField(max_length=50)
    number_lost = models.CharField(max_length=50)
    group_type = models.CharField(max_length=50)

    ecoregion_domain = models.CharField(max_length=50)
    ecoregion_division = models.CharField(max_length=50)
    terrain = models.CharField(max_length=50)

    total_hours = models.CharField(max_length=50)
    notify_hours = models.CharField(max_length=50)
    search_hours = models.CharField(max_length=50)

    comments = models.CharField(max_length=5000)
    LayerField = models.CharField(max_length=50)
    UploadedLayers = models.BooleanField()

    showfind = models.BooleanField()
    upright_lat = models.CharField(max_length=30)
    upright_lon = models.CharField(max_length=30)
    downright_lat = models.CharField(max_length=30)
    downright_lon = models.CharField(max_length=30)
    upleft_lat = models.CharField(max_length=30)
    upleft_lon = models.CharField(max_length=30)
    downleft_lat = models.CharField(max_length=30)
    downleft_lon = models.CharField(max_length=30)
    findx = models.CharField(max_length=10)
    findy = models.CharField(max_length=10)

    sidecellnumber = models.CharField(max_length=30)
    totalcellnumber = models.CharField(max_length=30)

    URL = models.CharField(max_length=1000)
    URLfind = models.CharField(max_length=1000)

    horstep = models.CharField(max_length=30)
    verstep = models.CharField(max_length=30)

    class Meta:
        db_table = 'mapscore_case'

    def GreatSphere(self,LatIn):
        """Calculate the longitude cellsize at this latitude.
        Uses a Great Sphere approximation.

        """

        lat = math.radians(float(LatIn))
        distance_traveled = 5
        earth_radius_meters = 6372.8 * 1000

        num = 1 - math.cos(distance_traveled / earth_radius_meters)
        denom = math.pow(math.cos(lat), 2)
        full = 1 - (num / denom)
        rad_diff = math.acos(full)

        return math.degrees(rad_diff)

    def initialize(self):
        SideLength_km_ex = 25         # length of bounding box in km
        cellside_m = 5                # length of cell (pixel) in m
        SideLength_m_ex = SideLength_km_ex * 1000
        self.sidecellnumber = SideLength_m_ex/cellside_m + 1
        self.totalcellnumber = math.pow(self.sidecellnumber, 2)
        last_lat = float(self.lastlat)
        last_lon = float(self.lastlon)
        find_lat = float(self.findlat)
        find_lon = float(self.findlon)

        #Generate boundary Coordinates
        hor_step = self.GreatSphere(last_lat)
        ver_step = float(cellside_m) / 111122.19769903777
        self.horstep = hor_step
        self.verstep = ver_step

        val = (SideLength_m_ex / cellside_m) / 2
        hor_scale = val * hor_step
        ver_scale = val * ver_step

        rightbound = last_lon + (hor_step / 2) + hor_scale
        leftbound = last_lon - (hor_step / 2) - hor_scale
        upbound = last_lat + (ver_step / 2) + ver_scale
        lowbound = last_lat - (ver_step / 2) - ver_scale

        # Corners
        self.upright_lat = upbound
        self.upright_lon = rightbound
        self.upleft_lat = upbound
        self.upleft_lon = leftbound
        self.downright_lat = lowbound
        self.downright_lon = rightbound
        self.downleft_lat = lowbound
        self.downleft_lon = leftbound

        # Generate List Grids

        # TODO crt 2014-03: Can't we just do:
        # N = self.sidecellnumber
        # LonList = [leftbound + i*Hor_step for i in range(N)]
        # LatList = [upbound - i*ver_step for i in range(N)]
        #
        # Wait. We dont' even need these.
        # LonList = []
        # LonList.append(leftbound)
        # for i in (range(self.sidecellnumber)):
        #     LonList.append(LonList[i] + Hor_step)

        # LatList = []
        # LatList.append(upbound)
        # for i in (range(self.sidecellnumber)):
        #     LatList.append(LatList[i] - ver_step)

        # Screen Coords of FindLoc, with (0,0) in the top left
        self.findx = int((find_lon - leftbound) / hor_step)
        self.findy = int((upbound - find_lat) / ver_step)
        self.generate_image_url()

        # We used to show FindLoc only for the first 20 trials
        # but right now we are always showing it.
        #if self.id <= 20:
        #    self.showfind = True
        self.showfind = True

        # Try to fill in a missing Total_Time
        if str(self.total_hours).lower() == 'unknown':
            try:
                self.total_hours = (float(self.notify_hours) +
                                    float(self.search_hours))
            except ValueError:
                pass

        # Set Layer Location
        self.LayerField  = "Layers/%s_%s.zip" % (self.id, self.case_name)
        self.UploadedLayers = False

    def generate_image_url(self):
        """Generates image URL using Google Maps """
        attrs = self.__dict__
        self.URL = GOOGLE_STATIC_MAPS_URL_TEMPLATE.format(**attrs)
        self.URLfind = GOOGLE_STATIC_MAPS_URL_FIND_TEMPLATE.format(**attrs)


class Test(models.Model):

    test_case = models.ForeignKey(Case)
    test_name = models.CharField(max_length=30)
    test_rating = models.CharField(max_length=10, default='unrated')
    active = models.BooleanField(default=False)
    ID2 = models.CharField(max_length=100)
    nav = models.CharField(max_length=2, default=0)
    show_instructions = models.BooleanField(default=True)

    Validated = models.BooleanField()
    test_url = models.CharField(max_length=300)
    test_url2 = models.CharField(max_length=300)
    grayscale_path = models.CharField(max_length=300)
    grayrefresh = models.CharField(max_length=10, default=0)

    class Meta:
        db_table = 'test'

    # TODO: Figure out why this is return str type?
    def __unicode__(self):
        return str(self.test_name)

    def getmap(self):
        """Load the image and force it to be grayscale.
           Return a values as a (5001,5001) numpy array.
           This should be faster than the old 'for' loop checking pixels for RGB.

           TODO:
             * If the image is already grayscale, does this still convert?
             * Can we open direct to numpy array and avoid second conversion?
             * What if Image throws and exception?

        """
        path = self.grayscale_path
        img = Image.open(path).convert(mode="L")
        values = np.array(img.getdata())
        return values.reshape((5001, 5001))

    def rate(self):
        """Scores the image using Rossmo's metric: r = (n+.5m)/N; R = (.5-r)/.5

        We assume each pixel has the probability for that cell, or at least a
        value monotonically related to the probability.
            n = the #pixels with probability greater than the find location
            m = the #pixels with probability equal to that of the find location
            N = total #pixels in the image

        Rossmo's R ranges from -1..1.  Using Koester's correction, random or single-color
        maps get a score of 0.

        For find locations outside the bounding box, we simply compare the total
        probability inside the bounding box with the remainder "Rest of World"
        or ROW probability. If the model probs sum to 1 or more (which it will
        for PNG images), then we use a conventional split with ROW=5% and
        bounding box=95%.  In that case, r = .95 and R = -.9.

        2014-02:
         * Refactored load to getmap(), and removed duplicate code.
         * Replaced inefficient loop with numpy ops. Thanks msonwalk for template!
         * Handled case where findloc is outside the image. (ROW)

        """
        x,y = int(self.test_case.findx), int(self.test_case.findy)
        values = self.getmap()            # a numpy array
        N = np.size(values)               # num pixels
        assert(N == 5001*5001)

        if (0 <= x <= 5000) and (0 <= y <= 5000):
            p = values[x, y]              # prob at find location
            n = np.sum(values > p)        # num pixels > p
            m = np.sum(values == p)       # num pixels == p
            r = (n + m / 2.) / N            # Uses decimal to force float division
        else:
            p = 1. - np.sum(values)       # prob for ROW
            if p < 0 or p > 1:            # model didn't consider ROW
                p = .05                   # assume 5% for ROW
            r = 1 - p                       # Assume we search bbox before ROW

        R = (.5 - r) / .5                 # Rescale to -1..1

        # Store result and update model
        self.test_rating = round(R,6)
        self.save()
        self.model_set.all()[0].update_rating()
        return 0                        # could return r,R


class Model(models.Model):
    """A Model has a name, description, and scores on its test cases."""

    completed_cases = models.IntegerField(max_length=30, default=0)
    name_id = models.CharField(max_length=30)
    #gridvalidated = models.BooleanField()
    tests = models.ManyToManyField(Test, through='TestModelLink')
    avgrating = models.CharField(max_length=10, default='unrated')
    ID2 = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        db_table = 'model'

    def update_rating(self):
        """Recalculate the model's ratings, ignoring any active tests.
        If there are no completed tests, sets avgrating to 'unrated'.
        """
        counter = 0
        add = 0.0
        tests = [x for x in self.tests.all() if x.active == False]
        if not tests:
            self.avgrating = 'unrated'
        else:
            ratings = [float(t.test_rating) for t in tests]
            self.avgrating = round(np.average(ratings), 5)

        self.save()


class Account(models.Model):
    username = models.CharField(max_length=30)
    institution_name = models.CharField(max_length=40)
    Website = models.URLField()

    photosizex = models.IntegerField(default=0)
    photosizey = models.IntegerField(default=0)
    photolocation = models.CharField(max_length=30)
    photourl = models.CharField(max_length=30)

    account_models = models.ManyToManyField(Model, through='ModelAccountLink')
    ID2 = models.CharField(max_length=100)

    sessionticker = models.IntegerField(default=0)
    completedtests = models.IntegerField(default=0)
    deleted_models = models.IntegerField(default=0)
    profpicrefresh = models.IntegerField(default=0)

    class Meta:
        db_table = 'account'


class ModelAccountLink(models.Model):
    account = models.ForeignKey(Account)
    model = models.ForeignKey(Model)

    class Meta:
        db_table = "model_account_link"


class TestModelLink(models.Model):
    test = models.ForeignKey(Test)
    model = models.ForeignKey(Model)

    class Meta:
        db_table = 'test_model_link'


class Mainhits(models.Model):
    hits = models.IntegerField(max_length=10, default=0)

    class Meta:
        db_table = 'mainhits'

class TerminatedAccounts(models.Model):
    username = models.CharField(max_length=30)
    sessionticker = models.CharField(max_length=30)
    completedtests = models.CharField(max_length=30)
    institution_name = models.CharField(max_length=30)
    modelsi = models.CharField(max_length=30)
    deleted_models = models.CharField(max_length=10)

    class Meta:
        db_table = 'terminated_accounts'