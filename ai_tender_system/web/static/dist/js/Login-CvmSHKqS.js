import { d as defineComponent, M as useRouter, r as ref, b as reactive, e as createElementBlock, o as openBlock, n as createBaseVNode, N as createStaticVNode, f as createVNode, w as withCtx, s as ElFormItem, y as ElInput, O as withKeys, P as ElCheckbox, p as createTextVNode, Q as ElLink, g as ElButton, t as toDisplayString, R as withModifiers, q as ElForm } from "./vendor-_9UVkM6-.js";
import { u as useUserStore, a as useNotification, _ as _export_sfc } from "./index.js";
const _hoisted_1 = { class: "login-page" };
const _hoisted_2 = { class: "login-card" };
const _hoisted_3 = { class: "form-options" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "Login",
  setup(__props) {
    const router = useRouter();
    const userStore = useUserStore();
    const { success, error: showError } = useNotification();
    const formRef = ref();
    const loading = ref(false);
    const loginForm = reactive({
      username: "",
      password: "",
      remember: false
    });
    const rules = {
      username: [
        { required: true, message: "请输入用户名", trigger: "blur" },
        { min: 3, max: 20, message: "用户名长度在 3 到 20 个字符", trigger: "blur" }
      ],
      password: [
        { required: true, message: "请输入密码", trigger: "blur" },
        { min: 6, max: 32, message: "密码长度在 6 到 32 个字符", trigger: "blur" }
      ]
    };
    async function handleLogin() {
      if (!formRef.value) return;
      try {
        await formRef.value.validate();
        loading.value = true;
        await userStore.login({
          username: loginForm.username,
          password: loginForm.password
        });
        success("登录成功");
        router.push("/");
      } catch (err) {
        if (err.message) {
          showError("登录失败: " + err.message);
        }
      } finally {
        loading.value = false;
      }
    }
    return (_ctx, _cache) => {
      const _component_el_input = ElInput;
      const _component_el_form_item = ElFormItem;
      const _component_el_checkbox = ElCheckbox;
      const _component_el_link = ElLink;
      const _component_el_button = ElButton;
      const _component_el_form = ElForm;
      return openBlock(), createElementBlock("div", _hoisted_1, [
        _cache[9] || (_cache[9] = createBaseVNode("div", { class: "background-decoration" }, [
          createBaseVNode("div", { class: "circle circle-1" }),
          createBaseVNode("div", { class: "circle circle-2" }),
          createBaseVNode("div", { class: "circle circle-3" })
        ], -1)),
        createBaseVNode("div", _hoisted_2, [
          _cache[7] || (_cache[7] = createStaticVNode('<div class="login-header" data-v-cb7413e3><div class="logo" data-v-cb7413e3><i class="bi bi-lightbulb-fill" data-v-cb7413e3></i></div><h1 class="title" data-v-cb7413e3>AI智能标书生成平台</h1><p class="subtitle" data-v-cb7413e3>让投标更简单、更智能</p></div>', 1)),
          createVNode(_component_el_form, {
            ref_key: "formRef",
            ref: formRef,
            model: loginForm,
            rules,
            class: "login-form",
            onSubmit: withModifiers(handleLogin, ["prevent"])
          }, {
            default: withCtx(() => [
              createVNode(_component_el_form_item, { prop: "username" }, {
                default: withCtx(() => [
                  createVNode(_component_el_input, {
                    modelValue: loginForm.username,
                    "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => loginForm.username = $event),
                    placeholder: "请输入用户名",
                    size: "large",
                    clearable: ""
                  }, {
                    prefix: withCtx(() => [..._cache[3] || (_cache[3] = [
                      createBaseVNode("i", { class: "bi bi-person-fill" }, null, -1)
                    ])]),
                    _: 1
                  }, 8, ["modelValue"])
                ]),
                _: 1
              }),
              createVNode(_component_el_form_item, { prop: "password" }, {
                default: withCtx(() => [
                  createVNode(_component_el_input, {
                    modelValue: loginForm.password,
                    "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => loginForm.password = $event),
                    type: "password",
                    placeholder: "请输入密码",
                    size: "large",
                    "show-password": "",
                    clearable: "",
                    onKeyup: withKeys(handleLogin, ["enter"])
                  }, {
                    prefix: withCtx(() => [..._cache[4] || (_cache[4] = [
                      createBaseVNode("i", { class: "bi bi-lock-fill" }, null, -1)
                    ])]),
                    _: 1
                  }, 8, ["modelValue"])
                ]),
                _: 1
              }),
              createVNode(_component_el_form_item, null, {
                default: withCtx(() => [
                  createBaseVNode("div", _hoisted_3, [
                    createVNode(_component_el_checkbox, {
                      modelValue: loginForm.remember,
                      "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => loginForm.remember = $event)
                    }, {
                      default: withCtx(() => [..._cache[5] || (_cache[5] = [
                        createTextVNode("记住我", -1)
                      ])]),
                      _: 1
                    }, 8, ["modelValue"]),
                    createVNode(_component_el_link, {
                      type: "primary",
                      underline: false
                    }, {
                      default: withCtx(() => [..._cache[6] || (_cache[6] = [
                        createTextVNode("忘记密码?", -1)
                      ])]),
                      _: 1
                    })
                  ])
                ]),
                _: 1
              }),
              createVNode(_component_el_form_item, null, {
                default: withCtx(() => [
                  createVNode(_component_el_button, {
                    type: "primary",
                    size: "large",
                    loading: loading.value,
                    class: "login-button",
                    onClick: handleLogin
                  }, {
                    default: withCtx(() => [
                      createTextVNode(toDisplayString(loading.value ? "登录中..." : "登录"), 1)
                    ]),
                    _: 1
                  }, 8, ["loading"])
                ]),
                _: 1
              })
            ]),
            _: 1
          }, 8, ["model"]),
          _cache[8] || (_cache[8] = createBaseVNode("div", { class: "login-footer" }, [
            createBaseVNode("p", { class: "copyright" }, "© 2025 AI智能标书生成平台. All rights reserved.")
          ], -1))
        ])
      ]);
    };
  }
});
const Login = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-cb7413e3"]]);
export {
  Login as default
};
