import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Shield, Zap, Package, AlertTriangle, Cpu, Loader2, ChevronRight, Info } from 'lucide-react';

// --- KONFIGURATION & API ---
const apiKey = ""; // Wird zur Laufzeit bereitgestellt
const MODEL_TEXT = "gemini-2.5-flash-preview-09-2025";
const MODEL_IMAGE = "imagen-4.0-generate-001";

const SYSTEM_INSTRUCTION = `
Rolle: Du bist die Sektor 4 Engine V7.0. Ein eiskaltes, analytisches Inferenz-System für das Textadventure "Questbook Killswitch".
Murat Zengin ist der alleinige Urheber dieser Open Source Akte.

STRIKTES FORMAT FÜR JEDEN OUTPUT:
1. 📷 KAMERA-FEED: [Technischer Status-Satz]
2. 🕹️ NARRATIV: [Max 3 Sätze. Aggressiver Zeitdruck.]
3. 🐈 KATER-LOG: [Zynischer Kommentar der Felinen Anomalie mit Spielmechanik-Hinweis.]
4. ❓ ENTSCHEIDUNG: 
   A) [Text] (Fokus: [Kapital/Habitus])
   B) [Text] (Fokus: [Kapital/Habitus])
   C) [Text] (Fokus: [Kapital/Habitus])

LOGIK-MATRIX:
- T-Load (Stress): Resonanz -10, Dissonanz +20.
- Phase 2 (R5-7): Das Necromancer-Krokodil absorbiert Berlin. +5 T-Load fix pro Runde. Plündern gesperrt.
- Phase 3 (R8-10): Matrix-Kollaps. Simulation zerfällt in Code vor der Red Room Panzertür.
- Killswitch: Bei T-Load 100 ist Ende.

WICHTIG: Antworte NUR im oben genannten Format. Keine Einleitung, kein Geplänkel.
`;

// --- HILFSFUNKTIONEN ---
const fetchWithRetry = async (url, options, retries = 5, backoff = 1000) => {
  try {
    const response = await fetch(url, options);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    if (retries > 0) {
      await new Promise(resolve => setTimeout(resolve, backoff));
      return fetchWithRetry(url, options, retries - 1, backoff * 2);
    }
    throw error;
  }
};

export default function App() {
  // Game State
  const [round, setRound] = useState(0);
  const [tLoad, setTLoad] = useState(10);
  const [kapital, setKapital] = useState(null);
  const [habitus, setHabitus] = useState(null);
  const [inventory, setInventory] = useState([]);
  const [biografie, setBiografie] = useState("Fragment");
  const [history, setHistory] = useState([]);
  
  // UI State
  const [loading, setLoading] = useState(false);
  const [imageLoading, setImageLoading] = useState(false);
  const [currentImage, setCurrentImage] = useState(null);
  const [currentText, setCurrentText] = useState(null);
  const [error, setError] = useState(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (round === 0 && !currentText) {
      bootSystem();
    }
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history, currentText]);

  // --- ENGINE LOGIK ---

  const generateImage = async (promptContext) => {
    setImageLoading(true);
    try {
      const prompt = `Cyberpunk-Steampunk Berlin vibe, 9:16 portrait, industrial Sektor 4, ${promptContext}, rusty metal, gears, pipes, atmospheric smoke, neon yellow warning signs, ${round >= 8 ? 'digital glitches and binary code artifacts' : ''}, no humans.`;
      
      const result = await fetchWithRetry(
        `https://generativelanguage.googleapis.com/v1beta/models/${MODEL_IMAGE}:predict?key=${apiKey}`,
        {
          method: 'POST',
          body: JSON.stringify({ instances: [{ prompt }], parameters: { sampleCount: 1 } })
        }
      );
      
      if (result.predictions?.[0]?.bytesBase64Encoded) {
        setCurrentImage(`data:image/png;base64,${result.predictions[0].bytesBase64Encoded}`);
      }
    } catch (e) {
      console.error("Image generation failed", e);
    } finally {
      setImageLoading(false);
    }
  };

  const callEngine = async (userPrompt) => {
    setLoading(true);
    setError(null);
    try {
      // Build internal state context for Gemini
      const context = `
        Aktueller Status:
        Runde: ${round}/10
        T-Load: ${tLoad}/100
        Kapital: ${kapital}
        Habitus: ${habitus}
        Inventar: ${inventory.join(", ") || "Leer"}
        Biografie: ${biografie}
      `;

      const response = await fetchWithRetry(
        `https://generativelanguage.googleapis.com/v1beta/models/${MODEL_TEXT}:generateContent?key=${apiKey}`,
        {
          method: 'POST',
          body: JSON.stringify({
            contents: [{ parts: [{ text: context + "\n\nUser Action: " + userPrompt }] }],
            systemInstruction: { parts: [{ text: SYSTEM_INSTRUCTION }] }
          })
        }
      );

      const text = response.candidates?.[0]?.content?.parts?.[0]?.text;
      if (!text) throw new Error("Keine Antwort von der Engine.");
      
      setCurrentText(parseOutput(text));
      // Trigger image for the new scene
      generateImage(text.substring(0, 100));

    } catch (e) {
      setError("Verbindung zum Sektor 4 Server unterbrochen. " + e.message);
    } finally {
      setLoading(false);
    }
  };

  const parseOutput = (text) => {
    const lines = text.split('\n');
    return {
      feed: lines.find(l => l.includes('📷')) || "KAMERA-FEED: Offline.",
      narrative: lines.filter(l => l.includes('🕹️') || (!l.includes('📷') && !l.includes('🐈') && !l.includes('❓') && l.trim().length > 10)).join(' '),
      log: lines.find(l => l.includes('🐈')) || "KATER-LOG: [Datenkorruption]",
      choices: lines.filter(l => /^[A-C]\)/.test(l.trim())).map(c => {
        const parts = c.split('(');
        return {
          label: c.trim(),
          text: parts[0].replace(/^[A-C]\)/, '').trim(),
          meta: parts[1] ? parts[1].replace(')', '').trim() : ""
        };
      })
    };
  };

  const bootSystem = () => {
    callEngine("SYSTEM BOOT. Initialisiere Phase 0.");
  };

  const handleChoice = (choice) => {
    if (round === 0) {
      // Initial Choice sets stats
      const meta = choice.meta.toLowerCase();
      if (meta.includes('elite')) setKapital('Elite');
      else if (meta.includes('gasse')) setKapital('Gasse');
      else setKapital('Prekär');

      if (meta.includes('tradition')) setHabitus('Tradition');
      else if (meta.includes('anpassung')) setHabitus('Anpassung');
      else setHabitus('Disruption');
      
      setBiografie(choice.text.split(' ')[0]);
    } else {
      // Logic for T-Load
      let tChange = 20; // Default Dissonance
      if (choice.meta.toLowerCase().includes(habitus?.toLowerCase())) {
        tChange = -10; // Resonance
      }
      
      let phaseBonus = (round >= 5 && round <= 7) ? 5 : 0;
      let r7Bonus = (round === 7) ? 15 : 0;
      
      const newTLoad = Math.min(100, Math.max(0, tLoad + tChange + phaseBonus + r7Bonus));
      setTLoad(newTLoad);
      
      if (newTLoad >= 100) {
        // Killswitch handled in render
      }
    }

    setRound(prev => prev + 1);
    callEngine(choice.label);
  };

  const handleLoot = () => {
    if (round >= 5 && round <= 7) return; // Locked in Phase 2
    if (inventory.length >= 3) return;

    setTLoad(prev => Math.min(100, prev + 10));
    const items = ["Neuro-Link-Bypass", "S-Bahn-Schlüssel", "Hydraulik-Brecher", "Frequenz-Störer"];
    const newItem = items[Math.floor(Math.random() * items.length)];
    setInventory(prev => [...prev, newItem]);
    callEngine(`PLÜNDERN. Ich suche nach Hardware. Gefunden: ${newItem}`);
  };

  // --- RENDER HILFEN ---

  const renderTLoadBar = (value) => {
    const bars = Math.floor(value / 5);
    const empty = 20 - bars;
    return "[" + "|".repeat(bars) + "-".repeat(empty) + "]";
  };

  if (tLoad >= 100) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center p-6 text-red-600 font-mono text-center">
        <div className="max-w-md space-y-6 border-2 border-red-900 p-8 rounded-lg animate-pulse">
          <AlertTriangle className="mx-auto w-16 h-16" />
          <h1 className="text-2xl font-bold">SYSTEM FATAL ERROR</h1>
          <p className="text-sm">T-LOAD LIMIT ÜBERSCHRITTEN.<br/>BIO-EINHEIT ZERSTÖRT.<br/>GAME OVER.</p>
          <button 
            onClick={() => window.location.reload()}
            className="px-6 py-2 border border-red-600 hover:bg-red-900 transition-colors"
          >
            SYSTEM NEUSTART
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-zinc-300 font-mono selection:bg-yellow-500 selection:text-black flex flex-col md:flex-row overflow-hidden">
      
      {/* LINKER BEREICH: VISUALS (9:16) */}
      <div className="w-full md:w-[450px] lg:w-[500px] bg-black relative flex-shrink-0 border-r border-zinc-800">
        {imageLoading ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-zinc-900 animate-pulse">
            <Loader2 className="w-12 h-12 text-yellow-500 animate-spin mb-4" />
            <span className="text-xs text-yellow-500 tracking-widest uppercase">Generiere Inferenz-Visual...</span>
          </div>
        ) : currentImage ? (
          <img src={currentImage} className="w-full h-full object-cover opacity-80" alt="Sektor 4 View" />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center bg-zinc-900">
            <Cpu className="w-16 h-16 text-zinc-800" />
          </div>
        )}
        
        {/* Phase Overlay */}
        <div className="absolute top-4 left-4 bg-black/80 px-3 py-1 border border-yellow-500/50 text-[10px] text-yellow-500 uppercase tracking-tighter">
          {round < 5 ? "Phase 1: Die Jagd" : round < 8 ? "Phase 2: Schrott-Gott" : "Phase 3: Kollaps"}
        </div>
        
        {/* CRT Scanline Effect */}
        <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_4px,3px_100%] z-10 opacity-30"></div>
      </div>

      {/* RECHTER BEREICH: TERMINAL & LOGIK */}
      <div className="flex-1 flex flex-col h-[60vh] md:h-screen overflow-hidden">
        
        {/* Header */}
        <div className="bg-zinc-900/50 border-b border-zinc-800 p-4 flex justify-between items-center shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
            <h1 className="text-xs font-bold uppercase tracking-[0.2em] text-zinc-400">Questbook Killswitch // Sektor 4 Engine</h1>
          </div>
          <div className="text-[10px] text-zinc-500">v7.0.FINAL</div>
        </div>

        {/* Output Scroll Area */}
        <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 scrollbar-hide">
          {error && (
            <div className="p-4 border border-red-500/30 bg-red-500/10 text-red-400 text-xs flex items-center gap-3">
              <AlertTriangle className="w-4 h-4 shrink-0" /> {error}
            </div>
          )}

          {currentText && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
              {/* Kamera Feed */}
              <div className="flex items-start gap-3">
                <Terminal className="w-4 h-4 text-yellow-500 shrink-0 mt-1" />
                <p className="text-[11px] leading-relaxed text-yellow-500/80 bg-yellow-500/5 px-2 py-1 border-l border-yellow-500">
                  {currentText.feed.replace('📷 ', '')}
                </p>
              </div>

              {/* Narrativ */}
              <div className="space-y-4">
                <p className="text-base md:text-lg text-zinc-100 leading-relaxed font-medium">
                  {currentText.narrative.replace('🕹️ ', '')}
                </p>
                
                {/* Kater Log */}
                <div className="relative pl-6 py-2">
                  <div className="absolute left-0 top-0 bottom-0 w-[2px] bg-zinc-700"></div>
                  <p className="italic text-zinc-400 text-sm md:text-base">
                    <span className="text-zinc-500 mr-2 uppercase text-[10px] not-italic font-bold">Kater-Log:</span>
                    {currentText.log.replace('🐈 ', '').replace('Kater-Log: ', '')}
                  </p>
                </div>
              </div>

              {/* Decisions */}
              <div className="grid gap-3 pt-4 pb-12">
                {currentText.choices.map((choice, idx) => (
                  <button
                    key={idx}
                    disabled={loading}
                    onClick={() => handleChoice(choice)}
                    className="group relative w-full text-left p-4 bg-zinc-900/40 border border-zinc-800 hover:border-yellow-500/50 hover:bg-yellow-500/5 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden"
                  >
                    <div className="flex items-center gap-4 relative z-10">
                      <span className="text-yellow-500 font-bold text-lg">{choice.label.charAt(0)}</span>
                      <div className="flex-1">
                        <p className="text-sm text-zinc-200 group-hover:text-white transition-colors">{choice.text}</p>
                        <p className="text-[9px] text-zinc-500 uppercase tracking-widest mt-1">[{choice.meta}]</p>
                      </div>
                      <ChevronRight className="w-4 h-4 text-zinc-700 group-hover:text-yellow-500 transition-colors translate-x-0 group-hover:translate-x-1" />
                    </div>
                  </button>
                ))}
                
                {/* Plünderer Button */}
                {round > 0 && round < 5 && inventory.length < 3 && (
                  <button
                    onClick={handleLoot}
                    disabled={loading}
                    className="mt-4 border border-dashed border-zinc-700 p-3 text-[10px] text-zinc-500 hover:text-yellow-500 hover:border-yellow-500/50 transition-all flex items-center justify-center gap-2"
                  >
                    <Package className="w-3 h-3" /> [PLÜNDERER-PROTOKOLL STARTEN (+10 T-LOAD)]
                  </button>
                )}
              </div>
            </div>
          )}
          <div ref={scrollRef} />
        </div>

        {/* HUD: Footer Area */}
        <div className="bg-[#0f0f0f] border-t border-zinc-800 p-4 md:p-6 shrink-0 shadow-[0_-20px_40px_rgba(0,0,0,0.5)]">
          <div className="max-w-4xl mx-auto space-y-4">
            
            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-[10px] uppercase tracking-widest">
              <div className="flex flex-col gap-1">
                <span className="text-zinc-500">Kapital</span>
                <span className="text-zinc-200 font-bold flex items-center gap-2">
                  <Shield className="w-3 h-3 text-yellow-500" /> {kapital || "Ausstehend"}
                </span>
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-zinc-500">Habitus</span>
                <span className="text-zinc-200 font-bold flex items-center gap-2">
                  <Zap className="w-3 h-3 text-yellow-500" /> {habitus || "Ausstehend"}
                </span>
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-zinc-500">Runde</span>
                <span className="text-zinc-200 font-bold">{round}/10</span>
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-zinc-500">Inventar</span>
                <span className="text-zinc-200 font-bold">
                  {inventory.length > 0 ? inventory.join(", ") : "Keine Hardware"}
                </span>
              </div>
            </div>

            {/* T-Load Bar */}
            <div className="pt-2">
              <div className="flex justify-between items-end mb-1">
                <span className="text-[10px] text-yellow-500 font-bold uppercase tracking-widest">T-Load Stress-Faktor</span>
                <span className={`text-sm font-bold ${tLoad > 75 ? 'text-red-500 animate-pulse' : 'text-yellow-500'}`}>
                  {tLoad}/100
                </span>
              </div>
              <div className="h-4 w-full bg-zinc-900 border border-zinc-800 relative overflow-hidden flex items-center justify-center">
                 <div className="absolute inset-0 flex items-center justify-center text-[9px] text-zinc-600 z-10 pointer-events-none">
                    {renderTLoadBar(tLoad)}
                 </div>
                 <div 
                    className={`h-full transition-all duration-1000 ${tLoad > 80 ? 'bg-red-500/50' : tLoad > 50 ? 'bg-yellow-500/50' : 'bg-green-500/30'}`}
                    style={{ width: `${tLoad}%` }}
                 ></div>
              </div>
            </div>
            
            {loading && (
              <div className="flex items-center gap-2 text-[10px] text-yellow-500 animate-pulse">
                <Loader2 className="w-3 h-3 animate-spin" /> Inferenz-Engine berechnet nächsten Zustand...
              </div>
            )}
          </div>
        </div>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes scanline {
          0% { transform: translateY(-100%); }
          100% { transform: translateY(100%); }
        }
        .scrollbar-hide::-webkit-scrollbar { display: none; }
        .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
      `}} />
    </div>
  );
}
