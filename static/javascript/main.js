var myapp = angular.module("myapp", []);
myapp.controller("MainCtrl", ["$http", "$scope", function ($http, $scope) {
    // -----------------------------------------------------------------------------
    // Params
    $scope.current_todos = [];                  // All todos in current category and page
    $scope.categories = [];                     // All categories of current user
    $scope.active_category = {};                // Current category
    $scope.active_category_name = "";           // Current category name, cannot use $scope.active_category.name
    $scope.current_page = 1;                    // Current page
    $scope.current_total_page = 1;              // Current total page
    $scope.current_sort_type = "time_desc";     // Current sort type
    $scope.delete_warning_status = false;

    $scope.search_status = false;               // If current page in search status
    $scope.category_added = false;              // 用来判断是否有新增的category
    $scope.set_category_added = function () {
        $scope.category_added = false;
    };


    // -----------------------------------------------------------------------------
    // When page is loaded, get all categories, and get all todos in first category/page
    window.onload = function () {
        $http({
            method: "GET",
            url: "/category/get/"
        }).then(function (value) {
            $scope.categories = value.data;
            $scope.active_category = $scope.categories[0];
            $scope.active_category_name = $scope.active_category.name;
            $scope.current_total_page = $scope.active_category.page;
            document.getElementById("todo_content_input").focus();
            $scope.get_todo($scope.active_category.id, 1, 'time_desc');
    })
    };

    // Change category, parameter added means if the target category is new added
    $scope.change_category = function (target, added) {
        var current_category = document.getElementById("category" + $scope.active_category.id);
        if (target.tagName === 'LI' && (current_category !== target || $scope.search_status === true)){
            $scope.search_status = false;
            var target_id = target.id.replace("category","");
            $scope.categories.find(function (value) {
               if (value.id === parseInt(target_id)){
                   $scope.active_category = value;
                   $scope.active_category_name = value.name;
               }
            });
            if (current_category){current_category.classList.remove("active")}
            target.classList.add("active");
            $scope.current_page = 1;
            $scope.current_total_page = $scope.active_category.page;
            $scope.get_todo(target_id,1,$scope.current_sort_type);
            if (added === true){
                document.getElementById("active_category_name_input").focus();
            } else {
                document.getElementById("todo_content_input").focus();
            }
        }
    };

    // -----------------------------------------------------------------------------
    // calculate total page by the number of todos
    $scope.calc_page = function (n) {
        if (n > 0 && n % 15 === 0){
            return Math.floor(n/15);
        } else {
            return Math.floor(n/15) + 1;
        }
    };

    // -----------------------------------------------------------------------------
    // Get todos from server
    $scope.get_todo = function (category_id, page, sort_type) {
        $http({
        method: "GET",
        url: "/todo/get/",
        params: {
            "page": page,
            "category_id": category_id,
            "sort_type": sort_type
            }
        }).then(function (value) {
            $scope.current_todos = value.data;
        })
    };

    // -----------------------------------------------------------------------------
    // Add a task
    $scope.add_todo = function () {
        var current_category_id = $scope.active_category.id;
        var content = document.getElementById("todo_content_input").value.replace(/(^\s*)|(\s*$)/g, "");
        if (content.length === 0){return}
        $http({
            method: "POST",
            url: "/todo/add/",
            data: {
                "category_id": current_category_id,
                "content": content
            }
        }).then(function (value) {
            if (value.statusText === "OK"){
                document.getElementById("todo_content_input").value = "";
                $scope.active_category.total_todo = $scope.active_category.total_todo + 1;
                $scope.active_category.page = $scope.calc_page($scope.active_category.total_todo);
                $scope.current_total_page = $scope.active_category.page;
                $scope.current_page = 1;
                $scope.current_sort_type = "time_desc";
                document.getElementById("sort_btn_1").innerText = "创建时间";
                document.getElementById("sort_btn_2").innerText = "↓";
                $scope.get_todo(current_category_id, 1, "time_desc");
            }
        })
    };
    $scope.add_todo_enter = function (e) {
        var keycode = window.event?e.keyCode:e.which;
        if (keycode === 13) {
            // alert(1);
            $scope.add_todo();
        }
    };
    // -----------------------------------------------------------------------------
    // Add a category
    $scope.add_category = function () {
        $http({
            method: "POST",
            url: "/category/add/",
            data: {
                "name": "My Todo List"
            }
        }).then(function (value) {
            if (value.statusText === "OK"){
                $scope.category_added = true;
                var new_category = {
                    "id": value.data.id,
                    "name": "My Todo List",
                    "total_todo": 0,
                    "completed_todo": 0,
                    "page": 1
                };
                $scope.categories.push(new_category);
                var current_category = document.getElementById("category"+$scope.active_category.id);
                if (current_category){current_category.classList.remove("active")}
                $scope.active_category = new_category;
                $scope.active_category_name = "My Todo List";
                $scope.current_todos = [];
                $scope.current_page = 1;
                $scope.current_total_page = 1;
                document.getElementById("active_category_name_input").focus();
                // document.getElementById("active_category_name_input").select();
            }
        })
    };

    // -----------------------------------------------------------------------------
    // Delete a task
    $scope.delete_todo = function (todo) {
        $http({
            method: "POST",
            url: "/todo/delete/",
            data: {"todo_id": todo.id}
        }).then(function (value) {
            if (value.statusText === "OK"){
                if ($scope.current_todos.length === 1 && $scope.current_page > 1){
                        $scope.current_page = $scope.current_page - 1;
                        $scope.current_total_page = $scope.current_total_page - 1;
                    }
                if ($scope.search_status){
                    $scope.categories.find(function (value2) {
                       if(value2.id === todo.category_id){
                           value2.total_todo = value2.total_todo-1;
                           if(todo.status){
                              value2.completed_todo = value2.completed_todo-1;
                           }
                       }
                    });
                        $scope.search_todo();
                } else {
                    $scope.active_category.page = $scope.current_total_page;
                    $scope.active_category.total_todo = $scope.active_category.total_todo - 1;
                    if (todo.status){
                        $scope.active_category.completed_todo = $scope.active_category.completed_todo - 1;
                    }
                    $scope.get_todo($scope.active_category.id, $scope.current_page, $scope.current_sort_type);
                }
            }
        })
    };

    // -----------------------------------------------------------------------------
    // Delete a category
    $scope.delete_category = function () {
        $http({
            method: "POST",
            url: "/category/delete/",
            data: {"category_id": $scope.active_category.id}
        }).then(function (value) {
            if (value.statusText === "OK") {
                for (var i = $scope.categories.length - 1; i >= 0; i--) {
                    if ($scope.categories[i].id === $scope.active_category.id) {
                        $scope.categories.splice(i, 1);
                    }
                }
                $scope.active_category = $scope.categories[0];
                $scope.active_category_name = $scope.active_category.name;
                $scope.get_todo($scope.active_category.id, 1, $scope.current_sort_type);
                // Delete a category does not lead to repeatFinish
                var current_category = document.getElementById("category"+$scope.active_category.id);
                console.log(current_category);
                current_category.classList.add("active");
                document.getElementById("todo_content_input").focus();
                $scope.delete_warning_status = false;
            }
        })
    };

    // Change task's status, use edit-task api
    $scope.change_todo_status = function (target, todo) {
        $http({
            method: "POST",
            url: "/todo/edit/",
            data: {'todo_id': todo.id,'status': ''}
        }).then(function (value) {
            if (value.statusText === "OK"){
                // target.innerText = value.data.status;
                if(value.data.status===true){
                    if ($scope.search_status){
                        $scope.categories.find(function (value2) {
                            if (value2.id === todo.category_id){
                                value2.completed_todo = value2.completed_todo + 1;
                            }
                        })
                    } else {
                        $scope.active_category.completed_todo = $scope.active_category.completed_todo + 1;
                    }
                    todo.status = true;
                } else {
                    if ($scope.search_status){
                        $scope.categories.find(function (value2) {
                            if (value2.id === todo.category_id){
                                value2.completed_todo = value2.completed_todo - 1;
                            }
                        })
                    } else {
                        $scope.active_category.completed_todo = $scope.active_category.completed_todo - 1;
                    }
                    todo.status = false;
                }
            }
        })
    };

    // Change page, use get-task api
    $scope.change_page = function (target) {
        if (target === 'previous' && $scope.current_page > 1 ){
            $scope.current_page = $scope.current_page - 1;
        } else if (target === 'next' && $scope.current_page < $scope.current_total_page){
            $scope.current_page = $scope.current_page + 1;
        } else if (target === 'page'){
            var new_page = document.getElementById("page_input").value;
            // console.log(document.getElementById("page_input"));
            if (isNaN(new_page) === false && parseInt(new_page) > 0 && parseInt(new_page) <= $scope.current_total_page){
                $scope.current_page = parseInt(new_page);
            }
        }
        if ($scope.search_status){
            $scope.search_todo();
        } else {
            $scope.get_todo($scope.active_category.id, $scope.current_page, $scope.current_sort_type);
        }
    };

    // Search task, use get-task api
    $scope.search_todo = function () {
        // $scope.search_status = true;
        var kw = document.getElementById("search_key_word").value;
        if ($scope.search_status === false){
            $scope.search_status = true;
            $scope.current_page = 1;
        }
        $http({
            method: "GET",
            url: "/todo/get/",
            params: {
                "kw": kw,
                "page": $scope.current_page,
                "sort_type": $scope.current_sort_type
            }
        }).then(function (value) {
            if (value.statusText === "OK"){
                $scope.current_todos = value.data.todos_list;
                $scope.current_total_page = $scope.calc_page(value.data.total_result);
                $scope.active_category_name = "搜索 " + kw;
                var active_category = document.getElementById("category"+$scope.active_category.id);
                if (active_category){
                    active_category.classList.remove("active");
                    $scope.active_category_id = "category"; //Delete active when firstly into search status
                }
            }
        })
    };

    // Change sort type by two btn
    $scope.change_sort_type = function (v) {
        if (parseInt(v) === 1){
            if ($scope.current_sort_type.startsWith("time")){
                $scope.current_sort_type = $scope.current_sort_type.replace("time", "complete");
                document.getElementById("sort_btn_1").innerText = "完成情况"
            } else if ($scope.current_sort_type.startsWith("complete")){
                $scope.current_sort_type = $scope.current_sort_type.replace("complete", "time");
                document.getElementById("sort_btn_1").innerText = "创建时间"
            }
        } else {
            if ($scope.current_sort_type.endsWith("desc")){
                $scope.current_sort_type = $scope.current_sort_type.replace("desc", "asc");
                document.getElementById("sort_btn_2").innerText = "↑"
            } else if ($scope.current_sort_type.endsWith("asc")){
                $scope.current_sort_type = $scope.current_sort_type.replace("asc", "desc");
                document.getElementById("sort_btn_2").innerText = "↓"
            }
        }
        if ($scope.search_status === false){
            $scope.get_todo($scope.active_category.id, $scope.current_page, $scope.current_sort_type);
        } else {
            $scope.search_todo();
        }
    };
    
    //
    $scope.change_delete_status = function () {
        $scope.delete_warning_status = !$scope.delete_warning_status;
    };

    document.getElementById("active_category_name_input").onblur = function (ev) {
        var name = $scope.active_category_name.replace(/(^\s*)|(\s*$)/g, "");
        if ($scope.active_category.name !== name && name.length > 0){
            $http({
                method: "POST",
                url: "/category/edit/",
                data: {
                'category_id': $scope.active_category.id,
                'name': name
                }
            }).then(function (value) {
                if (value.statusText === "OK"){
                    $scope.active_category_name = name;
                    $scope.active_category.name = name;
                }
            })
        } else {
            ev.target.value = $scope.active_category.name;
            $scope.active_category_name = $scope.active_category.name;
        }
    };

}]);

myapp.directive("repeatFinish", ["$timeout", function ($timeout) {
    return {
        restrict: "C",
        link: function (scope, element, attr) {
            if(scope.$last === true){
                // alert("new ng-repeat");
                if (scope.category_added === true){
                    scope.set_category_added();
                    $timeout(function () {
                        element[0].classList.add("active");
                    }, 10);
                } else {
                    if (scope.search_status === false) {
                       $timeout(function () {
                        // alert(scope.active_category.id);
                        var current_category = document.getElementById("category"+scope.active_category.id);
                        current_category.classList.add("active");
                    }, 10);
                    }
                }
            }
        }
    }
}]);

myapp.directive("deleteWaring", function () {
   return {
       restrict: "E",
       template: "<div id=\"mytodo-delete-warning\" ng-show=\"delete_warning_status\" ng-cloak>\n" +
       "<p>是否确认永久删除清单？</p>\n" +
       "<p>该操作无法撤销</p>\n" +
       "<button class=\"btn btn-danger pull-right\" ng-click=\"delete_category()\">确认</button>\n" +
       "<button class=\"btn pull-right\" ng-click=\"change_delete_status()\">取消</button>\n" +
       "</div>",
       replace: true
   }
});
