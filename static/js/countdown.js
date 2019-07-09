//倒计时的插件
$.fn.extend({
countdown:function(){
this.each(function() {
　　　　　　var dateStr = $(this).attr("end-date");
　　　　　　var endDate = new Date(dateStr.replace(/-/g,"/"));//取得指定时间的总毫秒数
　　　　　　var now = getseverdatetime();
            //如没有取到服务端时间，则取客户端时间
            if(now==undefined){
                alert('没有获取服务器时间')
　　　　　　　　now = new Date().getTime();
　　　　　　}
　　　　　　var tms = endDate - now;//得到时间差
　　　　　　if(tms<0){$.countdown.stop();return false;}
$.countdown.timers.push({tms:tms,content:$(this)});
$.countdown.start();
});
}
});
//倒计时的插件
$.countdown={
//倒计时容器，所有需要倒计时的时间都需要注册到这个容器中，容器中放的是一个object，object描述了倒计时的结束时间，以及显示时间的jquery对象(例如div)
timers:[],
//全局的一个倒计时状态，init表示初始化状态，start表示运行中状态，stop表示停止状态
status:'init',
//计算时间并定时刷新时间的方法，本插件的核心代码
takeCount:function(){
//如果定时器没有启动不执行
if(this.status != 'start')return;
setTimeout("$.countdown.takeCount()", 1000 );
var timers = this.timers;
for (var i = 0, j = timers.length; i < j; i++) {
//计数减一
timers[i].tms -= 1000;

//计算时分秒
var days = Math.floor(timers[i].tms / (1000 * 60 * 60 * 24));
var hours = Math.floor(timers[i].tms / (1000 * 60 * 60)) % 24;
var minutes = Math.floor(timers[i].tms / (1000 * 60)) % 60;
var seconds = Math.floor(timers[i].tms / 1000) % 60;
if (days < 0)days = 0;
if (hours < 0)hours = 0;
if (minutes < 0)minutes = 0;
if (seconds < 0) seconds = 0;
var newTimeText = days+"天"+hours+"小时"+minutes+"分"+seconds+"秒";
timers[i].content.text(newTimeText);
 if (days==0  && hours ==0 &&  minutes == 0 && seconds == 0 ){
     //秒杀开始
     var product_id  = $('#product_id').val();

     $('#J_SecKill').css('display','block');
     $('#J_SecKillready').css('display','none');
  }
}
},
//启动倒计时
start:function(){
if(this.status=='init'){
this.status = 'start';
this.takeCount();
}
},
//停止倒计时
stop:function(){
this.status = 'stop';
}
};

//获取服务器实时时间
// 常见的Ajax请求方法为GET,POST而这两种请求都可能会返回正文体,而发HEAD头则只会返回对应的头信息,不会有正文,且只要javascript可以执行,
// 就可以取当前域的地址作为请求地址,有一定的通用性,且避免了跨域的问题
function  getseverdatetime() {
    return new Date($.ajax({async:false}).getResponseHeader('Date'));
}