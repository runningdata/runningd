/**
 * Created by will on 15/12/9.
 */
/**
 * 解析URL参数
 */
function parseUrlParams(msg) {
    var params = {};
    var str = decodeURIComponent(msg);
    if(str.charAt(0) == '?')
        str = str.substring(1);
    var strs = str.split('&');
    for(var i=0;i < strs.length; i++) {
        if(strs[i].indexOf('=') > 0) {
            var temp = strs[i].split('=');
            params[temp[0]] = temp[1];
        } else if(strs[i] != null && strs[i] != ''){
            params[strs[i]] = true;
        }
    }

    return params;
}

/**
 * 判断模糊匹配字段是否合法
 */

function isRightName(name){
    if(name == null || name==""){
        return false;
    }else if(name == "undefined"){
        return false;
    }
    return true;

}

//对页面上编辑的字段进行合法想判断

function inputIsNull(data){
    if(data == null || data == ""){
        return false;
    }else if(data.length>100){
        return false;
    }
    return true;
}




