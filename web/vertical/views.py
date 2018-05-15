from django.http import JsonResponse
from django.shortcuts import render

from django.views import View

from web.vertical.models import Seed


class SeedListView(View):
    def get(self, request):
        seeds = Seed.objects.all()

        context = {
            'seeds': seeds,
        }
        return render(request, 'seeds.html', context = context)


class SeedView(View):
    def get(self, request):
        seed_id = request.GET.get('id')
        seed = Seed.objects.filter(id = seed_id).first()

        context = {
            'seed': seed,
        }
        return render(request, 'seed.html', context = context)


class AddSeedView(View):
    def get(self, request):
        context = {
            "add_pages": [
                {
                    "name": "artile_list",
                    "next": {
                        "type": "xpath",
                        "next_url_temp": "https://www.v2ex.com/t/{{article_id}}",
                        "next_url_regex": "t/(\\d+)",
                        "next_field": {
                            "//span[@class='item_title']/a/@href": "article"
                        }
                    },
                    "extract_field": {
                    },
                    "sample_urls": [
                        "https://www.v2ex.com/t/453364#reply145"
                    ],
                    "add_pages": [
                        {
                            "name": "article_detail",
                            "extract_type": "xpath",
                            "extract_field": {
                                "//div[@class='header']/h1/text()": "title"
                            }
                        }
                    ]
                }]
        }
        return render(request, 'addseed.html', context = context)

    def post(self, request, *args, **kwargs):
        print(request.POST.dict())
        seed = request.POST.get('seed_id', None)
        name = request.POST.get('name')
        description = request.POST.get('description')
        run_interval = request.POST.get('run_interval')
        rule_data = request.POST.get('rule_data')

        print('rule_data:%s' % rule_data)
        info = {
            'name': name,
            'description': description,
            'run_interval': run_interval,
            'rule_data': rule_data,
        }
        Seed.objects.update_or_create(id = seed, defaults = info)
        context = {
            # 'seed': seed,
            'status': 200
        }
        # return render(request, 'addseed.html', context = context)
        return JsonResponse(context)
