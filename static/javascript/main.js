var myapp = angular.module("myapp", []);
myapp.controller("MainCtrl", function ($http, $scope, $compile) {
    $scope.todo = "Angular";



    // Change dom functions
    window.onload = function () {
        document.getElementById("click-to-add").onclick = function () {
            var non_input_type = this;
            var input_type = document.createElement("input");
            input_type.setAttribute("placeholder", "添加待办事项");
            input_type.setAttribute("ng-keyup", "send($event)");
            input_type.className = "form-control";
            $compile(input_type)($scope);
            this.parentNode.replaceChild(input_type, non_input_type);
            input_type.focus();
            input_type.onblur = function () {
            if (input_type.value.length === 0){
                input_type.parentNode.replaceChild(non_input_type, input_type);
                }
            }
        }
    };
    $scope.send = function (e) {
        var keycode = window.event?e.keyCode:e.which;
        if (keycode === 13){
            alert("Add ToDO: " + e.target.value);
            e.target.value = "";
        }
    }
});
