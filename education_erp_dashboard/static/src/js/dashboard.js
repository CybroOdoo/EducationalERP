odoo.define("dashboard_dashboard.EducationalDashboard", function (require) {
    "use strict";
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;
    var rpc = require('web.rpc');
    var DashBoard = AbstractAction.extend({
        contentTemplate: 'EducationalDashboard',
     init: function(parent, context) {
                this._super(parent, context);
                this.dashboard_templates = ['MainSection'];
            },
     start: function() {
            var self = this;
            self.set("title", 'Dashboard');
            /* Showing the total exam result and total attendance and hiding
            the academic wise exam result and class wise attendance
            when loading */
            return self._super().then(function() {
            self.$('.academic_exam_result').hide();
            self.$('.exam_result').show();
            self.$('.class_attendance_today').hide();
            self.$('.total_attendance_today').show();
            /* Rendering the dashboard, graphs and filters */
                self.render_dashboards();
                self.render_graphs();
                self.render_filters();
            });
        },
    willStart: function(){
        var self = this;
        return self._super()
    },
    /* Function to render dashboard */
    render_dashboards: function() {
            var self = this;
            self.fetch_data()
            var templates = []
            var templates = ['MainSection'];
            _.each(templates, function(template) {
                self.$('.o_hr_dashboard').append(QWeb.render(template, {widget: self}))
            });
        },
    /* RPC call to fetch the count of applications, students, faculties,
    amenities and total exams */
        fetch_data: function() {
        var self = this;
        rpc.query({
            model: 'erp.dashboard',
            method: "erp_data",
        }).then(function (result) {
                self.$('#all_applications').append('<span>' + result.applications + '</span>');
                self.$('#all_students').append('<span>' + result.students + '</span>');
                self.$('#all_faculties').append('<span>' + result.faculties + '</span>');
                self.$('#all_amenities').append('<span>' + result.amenities + '</span>');
                self.$('#all_exams').append('<span>' + result.exams + '</span>');
            });
        },
        /* Click events for the tiles and change event for the filters */
        events:{
        'click #all_applications':'application_list',
        'click #all_students':'student_list',
        'click #all_faculties':'faculty_list',
        'click #all_amenities':'amenity_list',
        'click #all_attendance':'attendance_list',
        'click #exams':'exam_result',
        'click #timetable':'timetable',
        'click #promotion':'promotions',
        'change #select_period': function(e){
            e.preventDefault();
            if(e.target.value == 'select'){
            $('.academic_exam_result').hide();
            $('.exam_result').show();
            this.render_exam_result_pie();
            }
            else{
            $('.exam_result').hide();
            $('.academic_exam_result').show();
            this.get_academic_exam_result(e.target.value);
            }
          },
        'change #select_class': function(e){
            e.preventDefault();
            if(e.target.value == 'select'){
            $('.class_attendance_today').hide();
            $('.total_attendance_today').show();
            this.render_attendance_doughnut();
            }
            else{
             $('.total_attendance_today').hide();
             $('.class_attendance_today').show();
             this.get_class_attendance(e.target.value);
            }
          }
        },
    /* Functions that to show the details on click event */
    /* Click event function to show the applications */
        application_list:function(e){
        e.preventDefault();
             this.do_action({
                 type: "ir.actions.act_window",
                 name: "Applications",
                 res_model: "education.application",
                 views: [[false,'list'],[false,'form']],
                 target: 'current',
                 view_type : 'list',
                 view_mode : 'list',
               });
      },
    /* Click event function to show the students */
      student_list:function(e){
        e.preventDefault();
             this.do_action({
                 type: "ir.actions.act_window",
                 name: "Students",
                 res_model: "education.student",
                 views: [[false,'list'],[false,'form']],
                 target: 'current',
                 view_type : 'list',
                 view_mode : 'list',
               });
      },
    /* Click event function to show the faculties */
      faculty_list:function(e){
        e.preventDefault();
             this.do_action({
                 type: "ir.actions.act_window",
                 name: "Faculties",
                 res_model: "education.faculty",
                 views: [[false,'list'],[false,'form']],
                 target: 'current',
                 view_type : 'list',
                 view_mode : 'list',
               });
      },
    /* Click event function to show the amenities */
      amenity_list:function(e){
        e.preventDefault();
             this.do_action({
                 type: "ir.actions.act_window",
                 name: "Amenities",
                 res_model: "education.amenities",
                 views: [[false,'list'],[false,'form']],
                 target: 'current',
                 view_type : 'list',
                 view_mode : 'list',
               });
      },
    /* Click event function to show the attendance list */
      attendance_list:function(e){
        e.preventDefault();
             this.do_action({
                 type: "ir.actions.act_window",
                 name: "Attendance",
                 res_model: "education.attendance",
                 views: [[false,'list'],[false,'form']],
                 target: 'current',
                 view_type : 'list',
                 view_mode : 'list',
               });
      },
    /* Click event function to show the exam results */
      exam_result:function(e){
        e.preventDefault();
             this.do_action({
                 type: "ir.actions.act_window",
                 name: "Exam Result",
                 res_model: "education.exam",
                 views: [[false,'list'],[false,'form']],
                 target: 'current',
                 view_type : 'list',
                 view_mode : 'list',
               });
      },
    /* Click event function to show the time table */
      timetable:function(e){
        e.preventDefault();
             this.do_action({
                 type: "ir.actions.act_window",
                 name: "Timetable",
                 res_model: "education.timetable",
                 views: [[false,'list'],[false,'form']],
                 target: 'current',
                 view_type : 'list',
                 view_mode : 'list',
               });
      },
    /* Click event function to show the promotions */
      promotions:function(e){
        e.preventDefault();
             this.do_action({
                 type: "ir.actions.act_window",
                 name: "Student Promotions",
                 res_model: "education.student.final.result",
                 views: [[false,'list'],[false,'form']],
                 target: 'current',
                 view_type : 'list',
                 view_mode : 'list',
               });
      },
    /* Calling the functions to creates charts */
      render_graphs:function(){
      var self = this;
      self.render_total_application_graph();
      self.render_exam_result_pie();
      self.render_attendance_doughnut();
      self.render_rejected_accepted_applications();
      self.render_student_strength();
      self.render_class_wise_average_marks();
      },
    /* Calling the filter functions */
      render_filters:function(){
      var self = this;
      self.render_pie_chart_filter();
      self.render_doughnut_chart_filter();
      },
    /* Function to create a bar chart to show application counts in each
    academic year */
      render_total_application_graph:function(){
            var self = this
            var ctx = self.$(".application_count");
            rpc.query({
                model: "erp.dashboard",
                method: "get_all_applications",
            }).then(function (result) {
                var data = {
                    labels : Object.keys(result),
                    datasets: [{
                        label: 'Application',
                        data: Object.values(result),
                        backgroundColor: [
                            "#87cefa",
                            "#b0c4de",
                            "#20b2aa",
                        ],
                        borderColor: [
                            "#87cefa",
                            "#b0c4de",
                            "#20b2aa",
                        ],
                        borderWidth: 1
                    },]
                };
                //options to add appearance for the graph
                var options = {
                    responsive: true,
                    title: false,
                    scales: {
                        yAxes: [{
                            ticks: {
                                min: 0
                            }
                        }]
                    }
                };
                //create Chart class object
                new Chart(ctx, {
                    type: "bar",
                    data: data,
                    options: {
                        responsive:true,
                        maintainAspectRatio: false,
                        legend: {
                            display: false
                        },
                    }
                });
            });
      },
    /* Function to create a bar chart that shows the count of accepted and
    rejected applications */
      render_rejected_accepted_applications:function(){
            var self = this
            var ctx = self.$(".rejected_accepted_count");
            rpc.query({
                model: "erp.dashboard",
                method: "get_rejected_accepted_applications",
            }).then(function (result) {
                var data = {
                    labels : Object.keys(result),
                    datasets: [{
                        label: 'Application',
                        data: Object.values(result),
                        backgroundColor: [
                            "#778899",
                            "#f08080",
                        ],
                        borderColor: [
                            "#778899",
                            "#f08080",
                        ],
                        borderWidth: 1
                    },]
                };
                //options to add appearance for the graph
                var options = {
                    responsive: true,
                    title: false,
                    scales: {
                        yAxes: [{
                            ticks: {
                                min: 0
                            }
                        }]
                    }
                };
                //create Chart class object
                new Chart(ctx, {
                    type: "bar",
                    data: data,
                    options: {
                        responsive:true,
                        maintainAspectRatio: false,
                        legend: {
                            display: false
                        },
                    }
                });
            });
      },
    /* Function to create a pie chart that shows the exam results */
      render_exam_result_pie:function(){
            var self = this;
            var ctx = self.$(".exam_result")[0].getContext('2d');
            rpc.query({
                model: "erp.dashboard",
                method: "get_exam_result"
            }).then(function (result) {
                var data = {
                    labels : Object.keys(result),
                    datasets: [{
                        label: "Exam Result",
                        data: Object.values(result),
                        backgroundColor: [
                            "#003f5c",
                            "#dc143c"
                        ],
                        borderColor: [
                            "#003f5c",
                            "#dc143c",
                        ],
                        borderWidth: 1
                    },]
                };
                //options to add appearance for the graph
                var options = {
                    responsive: true,
                    title: false,
                    legend: {
                        display: true,
                        position: "bottom",
                        labels: {
                            fontColor: "#333",
                            fontSize: 16
                        }
                    },
                    scales: {
                        yAxes: [{
                            ticks: {
                                min: 0,
                            }
                        }]
                    }
                };
                /* create Chart class object */
                if(self.chart_total_result){
                    self.chart_total_result.destroy()
                }
                var chart_total_result = new Chart(ctx, {
                    type: "pie",
                    data: data,
                    options: options
                });
            });
        },
      /* Function to create a doughnut chart that shows attendance details */
        render_attendance_doughnut:function(){
            var self = this;
            var ctx = self.$(".total_attendance_today")[0].getContext('2d');
            rpc.query({
                model: "erp.dashboard",
                method: "get_attendance"
            }).then(function (result) {
                var data = {
                    labels : Object.keys(result),
                    datasets: [{
                        label: "Attendance",
                        data: Object.values(result),
                        backgroundColor: [
                            "#006400",
                            "#e9967a"
                        ],
                        borderColor: [
                            "#006400",
                            "#e9967a",
                        ],
                        borderWidth: 1
                    },]
                };
                //options to add appearance for the graph
                var options = {
                    responsive: true,
                    title: false,
                    legend: {
                        display: true,
                        position: "bottom",
                        labels: {
                            fontColor: "#333",
                            fontSize: 16
                        }
                    },
                    scales: {
                        yAxes: [{
                            ticks: {
                                min: 0,
                            }
                        }]
                    }
                };
                /* create Chart class object */
                if(self.chart_total_attendance){
                    self.chart_total_attendance.destroy()
                }
                var chart_total_attendance = new Chart(ctx, {
                    type: "doughnut",
                    data: data,
                    options: options
                });
            });
        },
      /* Function to create a line chart that shows the class wise student strength */
        render_student_strength:function(){
            var self = this
            var ctx = self.$(".student_strength");
            rpc.query({
                model: "erp.dashboard",
                method: "get_student_strength",
            }).then(function (result) {
                var data = {
                    labels : Object.keys(result),
                    datasets: [{
                        label: 'Student Strength',
                        data: Object.values(result),
                        backgroundColor: [
                            "#8b0000",
                        ],
                        borderColor: [
                            "#8b0000",
                        ],
                        borderWidth: 1
                    },]
                };
                //options to add appearance for the graph
                var options = {
                    responsive: true,
                    title: false,
                    scales: {
                        yAxes: [{
                            ticks: {
                                min: 0,
                            }
                        }]
                    }
                };
                //create Chart class object
                new Chart(ctx, {
                    type: "line",
                    data: data,
                    options: {
                        responsive:true,
                        maintainAspectRatio: false,
                        legend: {
                            display: false
                        },
                    }
                });
            });
      },
    /* Function to create a bar chart that shows the average marks in each class */
      render_class_wise_average_marks:function(){
            var self = this
            var ctx = self.$(".average_marks");
            rpc.query({
                model: "erp.dashboard",
                method: "get_average_marks",
            }).then(function (result) {
                var data = {
                    labels : Object.keys(result),
                    datasets: [{
                        label: 'Average Marks',
                        data: Object.values(result),
                        backgroundColor: [
                            "#cd5c5c",
                        ],
                        borderColor: [
                            "#cd5c5c",
                        ],
                        borderWidth: 1
                    },]
                };
                //options to add appearance for the graph
                var options = {
                    responsive: true,
                    title: false,
                    scales: {
                        yAxes: [{
                            ticks: {
                                min: 0,
                            }
                        }]
                    }
                };
                /* create Chart class object */
                new Chart(ctx, {
                    type: "bar",
                    data: data,
                    options: {
                        responsive:true,
                        maintainAspectRatio: false,
                        legend: {
                            display: false
                        },
                    }
                });
            });
      },
    /* Function to add the filter option */
      render_pie_chart_filter:function(){
      var self = this
      rpc.query({
                model: "erp.dashboard",
                method: "get_academic_year",
            }).then(function (result) {
                  $('#select_period').append('<option value=' + 'select' + '>' + 'Total Result' + '</option>')
                for (let key in result){
                  $('#select_period').append('<option value=' + key + '>' + result[key] + '</option>')
            }
      })
    },
   /* Function to get academic wise exam result and to create chart accordingly */
    get_academic_exam_result:function(academic_year){
      var self = this;
      var ctx = self.$(".academic_exam_result")[0].getContext('2d');
      rpc.query({
                model: "erp.dashboard",
                method: "get_academic_year_exam_result",
                args: [academic_year]
            }).then(function (result) {
            var data = {
                    labels : Object.keys(result),
                    datasets: [{
                        label: "Exam Result",
                        data: Object.values(result),
                        backgroundColor: [
                            "#003f5c",
                            "#dc143c"
                        ],
                        borderColor: [
                            "#003f5c",
                            "#dc143c",
                        ],
                        borderWidth: 1
                    },]
                };
                //options to add appearance for the graph
                var options = {
                    responsive: true,
                    title: false,
                    legend: {
                        display: true,
                        position: "bottom",
                        labels: {
                            fontColor: "#333",
                            fontSize: 16
                        }
                    },
                    scales: {
                        yAxes: [{
                            ticks: {
                                min: 0,
                            }
                        }]
                    }
                };
            /* Create Chart class object */
                if(self.chart_academy_result){
                    self.chart_academy_result.destroy()
                }
                self.chart_academy_result = new Chart(ctx, {
                    type: "pie",
                    data: data,
                    options: options
                });
            });
      },
    /* Function to add filter option for doughnut chart */
      render_doughnut_chart_filter:function(){
      var self = this
      rpc.query({
                model: "erp.dashboard",
                method: "get_classes",
            }).then(function (result) {
                  $('#select_class').append('<option value=' + 'select' + '>' + 'Total Attendance' + '</option>')
                for (let key in result){
                  $('#select_class').append('<option value=' + key + '>' + result[key] + '</option>')
                  }
            })
      },
    /* Function to get class wise attendance and to create chart accordingly */
      get_class_attendance:function(clas){
      var self = this;
      var ctx = self.$(".class_attendance_today")[0].getContext('2d');
      rpc.query({
                model: "erp.dashboard",
                method: "get_class_attendance_today",
                args: [clas]
            }).then(function (result) {
            var data = {
                    labels : Object.keys(result),
                    datasets: [{
                        label: "Exam Result",
                        data: Object.values(result),
                        backgroundColor: [
                             "#006400",
                             "#e9967a"
                        ],
                        borderColor: [
                            "#006400",
                            "#e9967a"
                        ],
                        borderWidth: 1
                    },]
                };
                var options = {
                    responsive: true,
                    title: false,
                    legend: {
                        display: true,
                        position: "bottom",
                        labels: {
                            fontColor: "#333",
                            fontSize: 16
                        }
                    },
                    scales: {
                        yAxes: [{
                            ticks: {
                                min: 0,
                            }
                        }]
                    }
                };
              /* Create Chart class object */
                if(self.chart_class_attendance){
                    self.chart_class_attendance.destroy()
                }
                self.chart_class_attendance = new Chart(ctx, {
                    type: "doughnut",
                    data: data,
                    options: options
                });
            });
      },
    })
    core.action_registry.add('erp_dashboard_tag', DashBoard);
    return DashBoard;
 });