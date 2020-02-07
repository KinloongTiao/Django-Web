"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from interface.view import *
from interface.add_user import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ctimes/', ctimes),
    path('interface/', interface),
    # path('GetStrategyList/', GetStrategyList),
    path('real-time/', real_time),
    path('main/',main),
    path('quant_simulate/',quant_simulate),
    path('quant_real/', quant_real),
    path('zhang_simulate/', zhang_simulate),
    path('zhang_real/', zhang_real),
    path('lifeng/',lifeng),
    path('cheng/',cheng),
    path('lifeng_netvalue/',lifeng_netvalue),
    path('research/', research),
    path('netvalue/',netvalue),
    path('testtop/',testtop),
    path('deletejson/',deletejson),
    path('stopstrategy/',stopStrategy),
    path('add/',add),
    path('result/',tanchuang),
    path('add_product/',add_product),
    path('add_account/',add_account),
    path('add_strategy/',add_strategy),
    path('correct_capital/',correct_capital),
    path('change_strategy/',change_strategy),
    path('add_user/',add_user),
    path('add_user_success/', add_user_success),
    path('login/', login),
    path('logout/',logout),
    path('concat/', concat_us),
    path('socket/',socket),
    path('settle_net_value/',netValueSettlement),

    path('postPnlPositionOrder/',post_all_pos_pnl_order),
    path('posttotalpnl/', posttotalpnl),
    path('posttotalpnl_makeup/', posttotalpnl_makeup),
    path('postorder/', postorder),
    path('postpositiondetail/', postpositiondetail),
    path('postanything/', postAnything),
    path('postCurrProdTs/',postCurrentProductTs),
    path('postCurrentProductReturn/',postCurrentProductReturn),
    path('manage/',management),

    path('newOrderApi/',get_new_order),
    path('refine_order/',refine_order),
    path('testApi/',testApi)



              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
