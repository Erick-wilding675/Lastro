import { useEffect,useState } from 'react'; import { api } from '../../lib/api'; import KpiGrid from '../../ui/KpiGrid';
export default function FaixaKpis(){const[kpis,setKpis]=useState(null);useEffect(()=>{api.kpis().then(setKpis).catch(()=>setKpis({}))},[]);return <KpiGrid kpis={kpis}/>}
