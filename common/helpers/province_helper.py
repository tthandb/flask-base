import pycountry


def detect_us_province_code(province):
    all_provinces = list(pycountry.subdivisions.get(country_code='US'))

    for province_data in all_provinces:
        if province == province_data.name:
            subdivision_code = province_data.code
            return subdivision_code.split('-')[1]
    return None


def detect_province_code(province, country_code):
    all_provinces = list(pycountry.subdivisions.get(country_code=country_code))

    for province_data in all_provinces:
        if province == province_data.name:
            subdivision_code = province_data.code
            return subdivision_code.split('-')[1]
    return None
