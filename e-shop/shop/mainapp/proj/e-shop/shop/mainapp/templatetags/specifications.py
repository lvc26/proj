from ..models import Skirt, Dress
from django import template
from django.utils.safestring import mark_safe



register = template.Library()

TABLE_HEAD = """
            <table class='table'>
              <tbody>
            """

TABLE_TAIL= """
              </tbody>
            </table>
            """

TABLE_CONTENT= """
                <tr>
                    <td>{name}</td>
                    <td>{value}</td>
                </tr>
                """
PRODUCT_SPEC= {
    'dress': {
        'Фасон': 'style',
        'Состав': 'structure',
        'Крой': 'сut',
        'Силуэт': 'silhouette',
        'Цвет': 'color',
        'Длина': 'length',
    },
    'skirt': {
        'Фасон': 'style',
        'Состав': 'structure',
        'Крой': 'сut',
        'Силуэт': 'silhouette',
        'Посадка': 'landing',
        'Длина': 'length',
    }
}

def get_product_spec(product, model_name):
    table_content=''
    for name, value in PRODUCT_SPEC[model_name].items():
        table_content += TABLE_CONTENT.format(name=name, value= getattr(product, value))
    return table_content


