
var Validator = {
   check: function(field, reg, extra) {
      var response;
      var rule = this.rule;
      rule.field = field;
      rule.value = field.value;
      rule.extra = extra;

      if(!reg || !reg.match(/^!/))
         response = rule.input();

      if(reg && !response && rule.value != '') {
         reg = reg.replace(/^!/, '');

         var mode = reg.split(/\s+/);
         for(var i = 0, m; m = mode[i]; i++) {
            m = m.replace(/([\d\-]+)?$/, '');
            response = rule[m](RegExp.$1);
            if(response) break;
         }
      }

      if(response)
         this.baloon.open(field, response);
   },

   submit: function(form) {
      this.allclose(form);
      var btns = new Array;

      for(var i = 0, f; f = form[i]; i++) {
         if(f.onblur)
            f.onblur();
         if(f.type == 'submit')
            btns.push(f);
      }

      for(var i = 0, f, z; f = form[i]; i++) {
         if(f._validbaloon && f._validbaloon.visible()) {
            while(z = btns.shift())
               this.baloon.open(z, this.rule.submit());
            return false;
         }
      }

      return true;
   },

   allclose: function(form) {
      for(var i = 0, f; f = form[i]; i++)
         if(f._validbaloon) f._validbaloon.close();
   }
};

Validator.baloon = {
   index: 0,

   open: function(field, msg) {
      if(!field._validbaloon) {
         var obj = new this.element(field);
         obj.create();
         field._validbaloon = obj;
         if(field.type == 'radio' || field.type == 'checkbox') {
            for(var i = 0, e; e = field.form[field.name][i]; i++)
               addEvent(e, 'focus', function() { obj.close(); });
         }
      }

      field._validbaloon.show(msg);
   },

   element: function() {
      this.initialize.apply(this, arguments);
   }
};

Validator.baloon.element.prototype = {
   initialize: function(field) {
      this.parent = Validator.baloon;
      this.field = field;
   },

   create: function() {
      var field  = this.field;

      var textarea_offset = 0
      if(field.type == 'textarea'){
   	textarea_offset = 100
      }

      var box = document.createElement('div');
      box.className = 'baloon';

      var offset = Position.offset(field);
      var top  = offset.y - 25;
      var left = offset.x - 20 + field.offsetWidth - textarea_offset;
      box.style.top  = top +'px';
      box.style.left = left+'px';

      var self = this;
      addEvent(box, 'click', function() { self.toTop(); });

      var bindClose = function() { self.close(); };
      var link = document.createElement('a');
      link.appendChild(document.createTextNode('X'));
      link.setAttribute('href', 'javascript:void(0);');
      addEvent(link, 'click', bindClose);
      addEvent(field, 'focus', bindClose);

      var msg = document.createElement('span');
      var div = document.createElement('div');
      div.appendChild(link);
      div.appendChild(msg);
      box.appendChild(div);
      document.body.appendChild(box);

      this.box = box;
      this.msg = msg;
   },

   show: function(msg) {
      var field = this.field;
      this.msg.innerHTML  = msg;

      this.box.style.display = '';
      this.toTop();

      if(field.type != 'radio' && field.type != 'checkbox') {
         var colors = new Array('#FF6666', '#FFAAAA', '#FF6666', '#FFAAAA');
         window.setTimeout(function() {
            if(colors.length > 0) {
               field.style.backgroundColor = colors.shift();
               window.setTimeout(arguments.callee, 70);
            }
         }, 10);
      }
   },

   close: function() {
      this.box.style.display = 'none';
      this.field.style.backgroundColor = '';
   },

   visible: function() {
      return (this.box.style.display == '');
   },

   toTop: function() {
      this.box.style.zIndex = ++ this.parent.index;
   }
};

Validator.rule = {
   msg: null,

   submit: function() {
      return this.msg.submit;
   },

   input: function() {
      if(this.field.type == 'radio' || this.field.type == 'checkbox') {
         for(var i = 0, e; e = this.field.form[this.field.name][i]; i++)
            if(e.checked) return;
         return this.msg.noselect;
      } else if(this.value == '')
         return (this.field.type == 'select-one') ? this.msg.noselect : this.msg.noinput;
   },

   mail: function() {
      if(!this.value.match(/^[\x01-\x7F]+@((([-a-z0-9]+\.)*[a-z]+)|(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))$/))
         return this.msg.mail;
   },

   equal: function() {
      if(this.field.form[this.extra].value && this.value != this.field.form[this.extra].value)
         return this.msg.unequal;
   },

   alphabet: function() {
      if(!this.value.match(/^[a-zA-Z\-\d]+$/))
         return this.msg.alphabet;
   },

   kana: function() {
      for(var i = 0;i < this.value.length;i++) {
         if(this.value.charAt(i) == ' ' || this.value.charAt(i) == '\u3000') continue;
         if(this.value.charAt(i) < '\u30A1' || this.value.charAt(i) > '\u30F6')
            return this.msg.kana;
      }
   },

   count: function(arg) {
      return this._range(arg, this.value.length, this.msg.count);
   },

   num: function(arg) {
      if(!this.value.match(/^[\d]+$/))
         return this.msg.num.nonumber;

      return this._range(arg, parseInt(this.value), this.msg.num);
   },

   check: function(arg) {
      var value = 0;
      for(var i = 0, e; e = this.field.form[this.field.name][i]; i++)
         if(e.checked) value += 1;

      return this._range(arg, value, this.msg.check);
   },

   _range: function(range, value, msg) {
      if(!range) return;

      var result = '';
      var c = (" "+range).split(/\-/);
      var min = parseInt(c[0]) || 0;
      var max = parseInt(c[1]) || 0;

      if(value != min && /^\d+$/.test(range))
         result = msg.unequal;
      else if(min == 0 && value > max)
         result = msg.too_big;
      else if(max == 0 && value < min)
         result = msg.too_small;
      else if(min > 0 && max > 0 && (value < min || value > max))
         result = msg.outofrange;

      return result.replace(/%1/g, min).replace(/%2/g, max);
   }
};

Validator.lang = {
   ja: {
      noselect:   '\u9078\u629E\u304C\u5FC5\u8981\u3067\u3059\u3002',
      noinput:    '\u5165\u529B\u304C\u5FC5\u8981\u3067\u3059\u3002',
      unequal:    '\u5165\u529B\u304C\u63C3\u3063\u3066\u3044\u307E\u305B\u3093\u3002',
   
      submit:     '\u5165\u529B\u30A8\u30E9\u30FC\u304C\u3042\u308A\u307E\u3059\u3002',
      mail:       '\u30E1\u30FC\u30EB\u30A2\u30C9\u30EC\u30B9\u306E\u5F62\u5F0F\u304C\u6B63\u3057\u304F\u3042\u308A\u307E\u305B\u3093\u3002',
      alphabet:   '\u30A2\u30EB\u30D5\u30A1\u30D9\u30C3\u30C8\u3001\u6570\u5B57\u3001' +
                     '- \u4EE5\u5916\u306F\u5165\u529B\u51FA\u6765\u307E\u305B\u3093\u3002',
      kana:       '\u5168\u89D2\u30AB\u30BF\u30AB\u30CA\u3067\u5165\u529B\u3057\u3066\u4E0B\u3055\u3044\u3002',
   
      count: {
         unequal:    '%1'+'\u6587\u5B57\u3067\u5165\u529B\u3057\u3066\u4E0B\u3055\u3044\u3002',
         too_big:    '%2'+'\u6587\u5B57\u4EE5\u5185\u3067\u5165\u529B\u3057\u3066\u4E0B\u3055\u3044\u3002',
         too_small:  '%1'+'\u6587\u5B57\u4EE5\u4E0A\u5165\u529B\u3057\u3066\u4E0B\u3055\u3044\u3002',
         outofrange: '%1'+'\u304B\u3089'+'%2'+'\u6587\u5B57\u306E\u9593\u3067\u5165\u529B\u3057\u3066\u4E0B\u3055\u3044\u3002'
      },
   
      num: {
         nonumber:   '\u6570\u5024\u3067\u5165\u529B\u3057\u3066\u4E0B\u3055\u3044\u3002',
         unequal:    '%1'+'\u3068\u5165\u529B\u3057\u3066\u4E0B\u3055\u3044\u3002',
         too_big:    '%2'+'\u4EE5\u4E0B\u306E\u5024\u3092\u5165\u529B\u3057\u3066\u4E0B\u3055\u3044\u3002',
         too_small:  '%1'+'\u4EE5\u4E0A\u306E\u5024\u3092\u5165\u529B\u3057\u3066\u4E0B\u3055\u3044\u3002',
         outofrange: '%1'+'\u304B\u3089'+'%2'+'\u306E\u9593\u3067\u5165\u529B\u3057\u3066\u4E0B\u3055\u3044\u3002'
      },
   
      check: {
         unequal:    '\u30C1\u30A7\u30C3\u30AF\u306F'+'%1'+'\u500B\u3057\u3066\u4E0B\u3055\u3044\u3002',
         too_big:    '\u30C1\u30A7\u30C3\u30AF\u306F'+'%2'+'\u500B\u307E\u3067\u3067\u3059\u3002',
         too_small:  '\u30C1\u30A7\u30C3\u30AF\u306F'+'%1'+'\u500B\u4EE5\u4E0A\u3057\u3066\u4E0B\u3055\u3044\u3002',
         outofrange: '\u30C1\u30A7\u30C3\u30AF\u306F'+'%1'+'\u500B\u304B\u3089'+'%2'+'\u500B\u307E\u3067\u3067\u3059\u3002'
      }
   }
};

Validator.rule.msg = Validator.lang.ja;

