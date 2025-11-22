const validatePhone = (rule, value, callback) => {
  if (!value) {
    callback();
    return;
  }
  const regex = /^1[3-9]\d{9}$/;
  if (regex.test(value)) {
    callback();
  } else {
    callback(new Error("请输入正确的手机号码"));
  }
};
const validateIdCard = (rule, value, callback) => {
  if (!value) {
    callback();
    return;
  }
  const regex = /^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/;
  if (regex.test(value)) {
    callback();
  } else {
    callback(new Error("请输入正确的身份证号码"));
  }
};
const validateEmail = (rule, value, callback) => {
  if (!value) {
    callback();
    return;
  }
  const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  if (regex.test(value)) {
    callback();
  } else {
    callback(new Error("请输入正确的邮箱地址"));
  }
};
export {
  validatePhone as a,
  validateIdCard as b,
  validateEmail as v
};
