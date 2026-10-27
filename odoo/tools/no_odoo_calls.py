# Erpiant non chiama mai i servizi esterni di odoo.com / openerp.com: il
# publisher che invia ogni settimana identificativo del database, numero di
# utenti, app installate e dati dell'azienda, i servizi IAP (autocompletamento
# delle aziende, arricchimento dei contatti, SMS, posta cartacea, immagini,
# testi generati), il controllo VIES fatto passare dai loro server e il loro
# proxy per lo SdI (la fatturazione elettronica passa da erpiant.com).
# Ogni richiesta verso quei domini fallisce come se il PC fosse senza rete:
# tutti i chiamanti gestiscono già requests.ConnectionError.
import logging
from urllib.parse import urlsplit

import requests

_logger = logging.getLogger(__name__)

BLOCKED_DOMAINS = ("odoo.com", "openerp.com")


def is_blocked(url):
    host = (urlsplit(url).hostname or "").lower().rstrip(".")
    return any(host == domain or host.endswith("." + domain) for domain in BLOCKED_DOMAINS)


_send = requests.Session.send


def _send_guarded(self, request, **kwargs):
    if is_blocked(request.url):
        host = urlsplit(request.url).hostname
        _logger.info("Chiamata verso %s non eseguita: disattivata in Erpiant", host)
        raise requests.exceptions.ConnectionError(
            "Chiamata verso %s disattivata in Erpiant" % host, request=request)
    return _send(self, request, **kwargs)


requests.Session.send = _send_guarded
