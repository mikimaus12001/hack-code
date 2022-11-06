import Home from './pages/home/Home';
import Enter from './pages/autorization/enter/Enter';
import Registration from './pages/autorization/registration/Registration';
import AllStartups from './pages/allstartups/AllStartups';
import New from './pages/users/new/New';
import SingleDPIR from './pages/users/singleDPIR/SingleDPIR';
import { BrowserRouter, Routes, Route } from "react-router-dom";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path='/'>
            <Route index element={<Home />} />
            <Route path='pages/allstartups' element={<AllStartups/>}/>
            <Route path='pages/autorization'>
              <Route path='enter' element={<Enter/>}/>
              <Route path='registration' element={<Registration/>}/>
            </Route>
            <Route path='pages/users'>
              <Route path='new' element={<New/>}/>
              <Route path='SingleDPIR' element={<SingleDPIR/>}/>
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
