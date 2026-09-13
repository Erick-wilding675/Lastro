import { useEffect, useState } from 'react';
import { assinarConexao, ROTULO_CONEXAO } from '../lib/conexao';
import { DEMO_FIXO } from '../lib/api';

/** Diz de onde vem o dado que está na tela. Substitui o antigo pill fixo
 *  "Motor conectado", que dizia isso mesmo com o backend fora do ar. */
export default function StatusConexao() {
  const [conexao, setConexao] = useState({ modo: DEMO_FIXO ? 'demo-fixo' : 'verificando', detalhe: '' });
  useEffect(() => assinarConexao(setConexao), []);

  const modo = DEMO_FIXO ? 'demo-fixo' : conexao.modo;
  const { texto, cor } = ROTULO_CONEXAO[modo] ?? ROTULO_CONEXAO.verificando;
  const titulo = modo === 'demo' && conexao.detalhe
    ? `API indisponível (${conexao.detalhe}) — exibindo dados sintéticos`
    : texto;

  return (
    <div className="status-pill" title={titulo}>
      <span className="status-dot" style={{ background: cor }} /> {texto}
    </div>
  );
}
