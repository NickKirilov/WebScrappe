import cases
import notices
import breaches

# Just to use both from on one place

notices.scrap_notices()
# to use the following function there must be a record with the notices numbers
notices.scrap_notices_details()

cases.scrap_cases()
# to use the following function there must be a record with the cases numbers
cases.scrap_cases_details()

breaches.scrap_breaches()
# to use the following function there must be a record with the breaches numbers
breaches.scrap_breaches_details()
