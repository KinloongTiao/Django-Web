$(document).ready(function(){
    var mun = $(".num").val();

    if (mun > 0) {//这个是判断它是不是大于0
        $(".num").css("color","red");
    }
    if(mun < 0) {//这个是判断它是不是小于0
        $(".num").css("color","green"); //添加颜色，可以是具体色值。如：#f60
    }
})