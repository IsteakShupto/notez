import { FormEvent, useRef } from "react";

function Login() {
  const emailRef = useRef<HTMLInputElement>(null);
  const passwordRef = useRef<HTMLInputElement>(null);
  const user = { email: "", password: "" };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (emailRef.current !== null) user.email = emailRef.current.value;
    if (passwordRef.current !== null) user.password = passwordRef.current.value;

    const response = await fetch("http://127.0.0.1:8000/api/login/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: user.email,
        password: user.password,
      }),
    });

    const data = await response.json();

    console.log(data);
  };

  return (
    <>
      <form onSubmit={handleSubmit} className="login-container">
        <h4 className="mb-3 text-center">Login to your account</h4>
        <div className="mb-3">
          <label htmlFor="login-email" className="form-label">
            Email
          </label>
          <input
            type="email"
            className="form-control"
            id="login-email"
            placeholder="name@email.com"
            ref={emailRef}
          />
        </div>

        <div className="mb-3">
          <label htmlFor="login-pass" className="form-label">
            Password
          </label>
          <input
            type="password"
            className="form-control"
            id="login-pass"
            placeholder="Enter your password"
            ref={passwordRef}
          />
        </div>

        <button className="login-button btn btn-primary" type="submit">
          Log in
        </button>

        <p className="mt-3 text-center">
          New to notez?
          <a href=""> Create an account here.</a>
        </p>
      </form>
    </>
  );
}

export default Login;
