var myapp = angular.module("myapp", []);
myapp.controller("MainCtrl", ["$http", function ($http) {
    var self = this;
    this.eml = "";
    this.psw = "";
    this.remember = false;
    this.login = function () {
        $http({
            method: "POST",
            url: "/login/",
            data: {
                "eml": self.eml,
                "psw": self.psw,
                "remember": self.remember
            }
        }).then(function (value) {
            if(value.statusText === "OK"){
                if(value.data === "OK"){
                    return
                } else {

                }
            }
        })
    };
}]);