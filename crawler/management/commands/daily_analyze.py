import logging
from datetime import date, timedelta

from django.core.management.base import BaseCommand

from crawler.analyzers.air_analyzer import AirAnalyzer
from crawler.analyzers.buy_queue import BuyQueue
from crawler.analyzers.cheap_rights_issue import CheapRightIssue
from crawler.analyzers.macd_cross import MACDCross
from crawler.analyzers.new_comer import NewComer
from crawler.analyzers.volume_analyzer import VolumeAnalyzer
from crawler.models import Share

import pandas as pd

logging.basicConfig(level=logging.DEBUG)


class Command(BaseCommand):
    help = 'Analyze Daily History'
    requires_migrations_checks = True

    def __init__(self, *args, **kwargs):
        self.daily_analyzers = [VolumeAnalyzer(), BuyQueue(), CheapRightIssue(), NewComer(), MACDCross(), AirAnalyzer()]
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('days', type=int, nargs='?', default=0)

    def handle(self, *args, **options):
        Share.DAY_OFFSET = options.get('days', 0)

        row_list = []
        for share in Share.objects.all():
            if share.daily_history.shape[0] > 0 and share.daily_history.iloc[-1]['Date'] >= date.today() - timedelta(
                    days=Share.DAY_OFFSET + 1):
                results = dict()
                for analyzer in self.daily_analyzers:
                    result = analyzer.analyze(share, share.daily_history_normalized, None)
                    if result:
                        results.update(result)

                if results:
                    row_list.append({"ticker": share.ticker, **results})
                    self.stdout.write("{}".format({share.ticker: results}))


        df = pd.DataFrame(row_list)

        from django.template import loader
        template = loader.get_template('daily_report.html')
        html_out = template.render({'date': date.today() - timedelta(days=Share.DAY_OFFSET + 1), 'daily_report_dataframe': df.to_html()})

        with open("report.html", 'w') as f:
            f.write(html_out)
