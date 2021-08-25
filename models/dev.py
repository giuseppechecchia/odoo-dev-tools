import logging

from odoo import (models, fields)  # , api

import requests
from requests.models import Response

from pathlib import Path
import os

_logger = logging.getLogger(__name__)


class DevTools(models.Model):

    _inherit = 'res.company'

    is_dev_environment = fields.Boolean(
        'Developer MODE',
        default=False
    )

    def init(self):
        self.loadRequestsOverride()

    def loadRequestsOverride(self):

        if self.is_developer_mode():
            requests.sessions.Session = DevRequestsOverride
            _logger.warning("**DEVELOPER MODE ON**")

    def is_developer_mode(self):

        status = False

        current_path = os.path.dirname(os.path.realpath(__file__))
        current_path = os.path.dirname(current_path)
        current_path = os.path.dirname(current_path)

        maintenance_file = Path(f"{current_path}/.maintenance")
        dev_file = Path(f"{current_path}/.dev")
        taroccone_file = Path(f"{current_path}/.taroccone")
        main_maintenance_file = Path(f"{os.getcwd()}/.maintenance")
        main_dev_file = Path(f"{os.getcwd()}/.dev")
        main_taroccone_file = Path(f"{os.getcwd()}/.taroccone")

        if maintenance_file.is_file() or \
                dev_file.is_file() or \
                taroccone_file.is_file() or \
                main_maintenance_file.is_file() or \
                main_dev_file.is_file() or \
                main_taroccone_file.is_file():
            status = True
        else:
            status = False

        try:
            self.update_env_status(status)
        except Exception as e:
            _logger.error(e)
        finally:
            return status

    def update_env_status(self, status):

        PENDING = 'pending'

        company = self.env['res.company'].search(
            [('name', 'like', 'FRMODA')]
        )

        previous_status = company.is_dev_environment

        try:
            company.write({
                'is_dev_environment': status
            })
        except Exception as e:
            _logger.critical(e)
            raise e

        # if developer mode is on do something
        if status is True:

            try:
                # deactivating jobs except dev's one
                self.start_maintenance()
            except Exception as e:
                # I'm raising because
                # without m2 dev env
                # we can broke lot of thing
                raise e
                _logger.error(e)

            result = self.drop_my_jobs()

            _logger.info(result)
        # check if is_dev_environment was True
        # mean that maintenance was finished
        else:
            if previous_status:
                job_maintenance_pool = self.env['queue.job.maintenance']
                job_maintenance_obj = job_maintenance_pool.search([])

                job_pool = self.env['queue.job']
                for job_maintenance in job_maintenance_obj:
                    _logger.info("job_maintenance:{},{}".format(
                        job_maintenance.name, job_maintenance.uuid))

                    job = job_pool.search(
                        [
                            ('uuid', '=', job_maintenance.uuid)
                        ]
                    )
                    job.write({
                        'state': PENDING
                    })
                    _logger.info("Switch to pending: %s" % job)
                    result = self.env.cr.execute("""
                        DELETE FROM queue_job_maintenance WHERE uuid = '{}'
                    """.format(job_maintenance.uuid))

    def start_maintenance(self):
        search_terms = [
            ('name', 'not like', '[TAROCCONE]'),
            ('name', 'not like', '[DEV]')
        ]
        self.env['ir.cron'].sudo().start_maintenance(search_terms)

    def drop_my_jobs(self):

        result = ""
        try:
            self.env.cr.execute(
                "SELECT name, uuid, * FROM queue_job where state <> 'done'"
            )
            jobs = self.env.cr.fetchall()

            if len(jobs) > 0:
                for job in jobs:
                    self.env.cr.execute("""
                        INSERT INTO queue_job_maintenance
                        (name, uuid) VALUES ('{}','{}')
                    """.format(job[0], job[1]))

                jobs = self.env.cr.execute("""
                    UPDATE queue_job SET state = 'done' where state <> 'done'
                """)

            result = 'ok'

        except Exception as e:
            result = repr(e)
        finally:
            result = 'Purge: ' + result

        return result

    def doTest(self):

        url = 'https://www.google.com/'
        response = requests.request("GET", url)

        dev_tools = self.env['res.company'].sudo().search([])

        _logger.error(dev_tools)
        _logger.error(response.status_code)
        _logger.error(response.text)

        return response

    def free_breakpoint(self):
        breakpoint()

        _logger.info('Welcome to the free breakpoint!')


class DevRequestsOverride(requests.Session):

    def request(self, *args, **kwargs):

        dummy_response = Response()
        dummy_response.code = "Method Not Allowed"
        dummy_response.error_type = "Method Not Allowed"
        dummy_response.status_code = 405
        dummy_response._content = \
            b'{ "reason" : "Development environment active" }'

        return dummy_response


class QueueJobMaintenance(models.Model):

    _name = 'queue.job.maintenance'
    _description = "Queue Job Maintenance"

    name = fields.Char(
        'Name'
    )
    uuid = fields.Char(
        'uuid'
    )
