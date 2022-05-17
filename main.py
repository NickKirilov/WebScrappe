import cases
import historical_cases
import notices
import breaches
import historical_breaches

# Just to use both from on one place

notices.scrap_notices()
# to use the following function there must be a record with the notices numbers
notices.scrap_notices_details()

cases.scrap_cases()
# to use the following function there must be a record with the cases numbers
cases.scrap_cases_details()

historical_cases.scrap_historical_cases()
# to use the following function there must be a record with the historical breaches numbers
historical_cases.scrap_historical_cases_details()

breaches.scrap_breaches()
# to use the following function there must be a record with the breaches numbers
breaches.scrap_breaches_details()

historical_breaches.scrap_historical_breaches()
# to use the following function there must be a record with the historical breaches numbers
historical_breaches.scrap_historical_breaches_details()
