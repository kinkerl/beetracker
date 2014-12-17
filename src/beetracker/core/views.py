
# Create your views here.

from core.models import Apiary, Hive, WhatToDoSeason

from core.osm import get_thing_by_tag, get_count_from_tag
from core.owm import get_current_weather_temp, get_current_weather_humidity
from django.db.models import Count, Avg
from django.shortcuts import render
from django.http import HttpResponse
import json
from decimal import Decimal

def heatmap_geojson(request):
    heatmap = Apiary.objects.values('latitude_approx', 'longitude_approx').annotate(Count("id")).order_by("-id__count")
    ret = []
    boxsize = Decimal(0.02)
    for poly in heatmap:
        heat = (float(poly["id__count"]) / float(heatmap[0]["id__count"]))

        dic = {}
        dic["type"] = "Feature"
        dic["properties"] = {"heat": heat}
        dic["geometry"] =  {
            "type": "Polygon",
            "coordinates": [[
                [float(poly["longitude_approx"]),  float(poly["latitude_approx"])],
                [float(poly["longitude_approx"]+boxsize),  float(poly["latitude_approx"])],
                [float(poly["longitude_approx"]+boxsize),  float(poly["latitude_approx"]+boxsize)],
                [float(poly["longitude_approx"]),  float(poly["latitude_approx"]+boxsize)],
                [float(poly["longitude_approx"]),  float(poly["latitude_approx"]+boxsize)]
            ]]
        }
        ret.append(dic)
    return HttpResponse(json.dumps(ret), content_type="application/json")



def dataviz(request):
    return render(request, "dataviz.html", {
        'chart_apiaries' : len(Apiary.objects.all()),
        'chart_hives' : len(Hive.objects.all()),
        'avg_lat'  : Apiary.objects.all().aggregate(Avg('latitude_approx'))['latitude_approx__avg'],
        'avg_long' : Apiary.objects.all().aggregate(Avg('longitude_approx'))['longitude_approx__avg'],
    
        })

def home(request):
    return render(request, "home.html", {})



def overview(request):
    return render(request, "overview.html", {'apiaries': Apiary.objects.all()})


def detail(request, aid):
    apiary = Apiary.objects.get(id=aid)
    whattodo = WhatToDoSeason.objects.all()

    natural_tree_species = get_thing_by_tag(apiary = apiary, tag_key="natural", tag_value="tree", thing=["species:de", "species", "name:botanical"])
    natural_tree_type = get_thing_by_tag(apiary = apiary, tag_key="natural", tag_value="tree", thing=["type"])
    number_trees = get_count_from_tag(apiary = apiary, tag_key="natural", tag_value="tree")
    leisure_parks = get_thing_by_tag(apiary=apiary, tag_key="leisure", tag_value="park")
    landuse_vineyards = get_thing_by_tag(apiary=apiary, tag_key="landuse", tag_value="vineyard")
    
    weather_temp = get_current_weather_temp(apiary=apiary)
    weather_humidity = get_current_weather_humidity(apiary=apiary)


    return render(request, "detail.html", {
        'apiary': apiary,
        'apiaries': Apiary.objects.all(),
        'number_trees': number_trees,
        'natural_tree_species': natural_tree_species, 
        'natural_tree_type': natural_tree_type,
        'leisure_park_chart': leisure_parks, 
        'landuse_vineyard_chart':landuse_vineyards,
        'weather_temp' : weather_temp,
        'weather_humidity' : weather_humidity,
        'whattodo' : whattodo
        })