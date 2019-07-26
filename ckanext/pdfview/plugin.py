import logging

import ckan.plugins as p
import ckan.lib.datapreview as datapreview
from ckan.plugins.toolkit import h, _

log = logging.getLogger(__name__)


class PdfView(p.SingletonPlugin):
    '''This extension views PDFs. '''

    if not p.toolkit.check_ckan_version('2.3'):
        raise p.toolkit.CkanVersionException(
            'This extension requires CKAN >= 2.3. If you are using a ' +
            'previous CKAN version the PDF viewer is included in the main ' +
            'CKAN repository.')

    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IResourceView, inherit=True)

    PDF = ['pdf', 'x-pdf', 'acrobat', 'vnd.pdf']
    proxy_is_enabled = False

    def info(self):
        return {'name': 'pdf_view',
                'title': 'PDF',
                'icon': 'file-text',
                'default_title': 'PDF',
                }

    def update_config(self, config):

        p.toolkit.add_public_directory(config, 'theme/public')
        p.toolkit.add_template_directory(config, 'theme/templates')
        p.toolkit.add_resource('theme/public', 'ckanext-pdfview')

    def configure(self, config):
        enabled = config.get('ckan.resource_proxy_enabled', False)
        max_size =config.get('ckanext.pdfview.max_size', '2000000')
        self.proxy_is_enabled = enabled
        self.custom_max_size = int(max_size)

    def can_view(self, data_dict):
        resource = data_dict['resource']
        format_lower = resource.get('format', '').lower()

        proxy_enabled = p.plugin_loaded('resource_proxy')
        same_domain = datapreview.on_same_domain(data_dict)

        pdf_size = resource.get('Size', 0)
        if pdf_size > self.custom_max_size:
            h.flash_notice(_('This PDF is too big for preview. Downloading the file is suggested'))
            return False
        if format_lower in self.PDF:
            return same_domain or proxy_enabled
        return False

    def view_template(self, context, data_dict):
        return 'pdf.html'
