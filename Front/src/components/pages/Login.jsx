// ... (imports e setup)

const Login = () => {
  const navigate = useNavigate(); 
  const [usuario, setUsuario] = useState(''); 
  const [senha, setSenha] = useState(''); 
  const [erroLogin, setErroLogin] = useState('');  
  const [loading, setLoading] = useState(false); 

  const handleLogin = async (e) => { // 🚨 Tornar async
    e.preventDefault();

    setLoading(true); 
    setErroLogin(''); 

    try {
      const response = await fetch('/login', { // 🚨 Chamada real ao backend
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: usuario, senha }),
      });

      const result = await response.json();

      if (response.ok && result.status === 'success') {
        // Sucesso no login
        // Na prática, armazenaríamos o token de autenticação (JWT)
        console.log("Login bem-sucedido:", result.user); 
        navigate('/home'); 
      } else {
        // Falha na autenticação
        setErroLogin(result.message || 'Erro desconhecido durante o login.');
      }
    } catch (error) {
      console.error('Erro de rede ou servidor:', error);
      setErroLogin('Não foi possível conectar ao servidor.');
    } finally {
      setLoading(false); // Finaliza o loading
    }
  };

  // ... (restante do componente)
};

export default Login;