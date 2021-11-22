import React from 'react';
import { Table, Card, Row, Col, Input } from 'antd';
import reqwest from 'reqwest';
import { ReactDOM } from 'react';
import { SearchOutlined } from '@ant-design/icons';
import axios from 'axios';

const API_URL = 'http://localhost:8000';
const { Search } = Input;

const columns = [
  {
    title: 'Match',
    dataIndex: 'Match',
    sorter: true,
    width: '33%',
  },
  {
    title: 'MatchStatus',
    dataIndex: 'MatchStatus',
    filters: [
      { text: 'LIVE', value: 'LIVE' },
      { text: 'PREMATCH', value: 'PREMATCH' },
    ],

  },
  {
    title: 'Competition',
    dataIndex: 'Competition',
    width: '20%',
    sorter: true,
  },
  {
    title: 'Market',
    dataIndex: 'Market',
    width: '20%',
  },
  {
    title: 'bookmaker 1',
    dataIndex: 'bookmaker 1',
    width: '10%',
    sorter: true,
  },
  {
    title: 'Odds 1',
    dataIndex: 'odds 1',
    sorter: true,
  },
  {
    title: 'bookmaker 2',
    dataIndex: 'bookmaker 2',
    width: '10%',
    sorter: true,
  },
  {
    title: 'Odds 2',
    dataIndex: 'odds 2',
    sorter: true,
  },
  {
    title: 'Margin',
    dataIndex: 'margin',
    sorter: true,
  },
];

const getRandomuserParams = params => ({
  results: params.pagination.pageSize,
  page: params.pagination.current,
  ...params,
});

function App() {

  const [data, setData] = React.useState([]);
  const [pagination, setPagination] = React.useState({
    current: 1,
    pageSize: 10,
  });
  const [loading, setLoading] = React.useState(false);
  const [value, setValue] = React.useState();
  const [totalData, setTotalData] = React.useState([]);

  React.useEffect(() => {
    fetchItem({ pagination });
  }, []);


  const handleTableChange = (_pagination, filters, sorter) => {
    console.log('here');

    if (pagination.current !== _pagination.current || pagination.pageSize !== _pagination.pageSize) { setPagination(_pagination); return; }
    console.log('there');
    fetchItem({
      sortField: sorter.field,
      sortOrder: sorter.order,
      pagination: _pagination,
      ...filters,
    });
    console.log('ok');
  };

  const fetchItem = (params = {}) => {

    setLoading(true);
    try {
      const url = `${API_URL}/api/customers/data`;
      axios.get(url, { params: getRandomuserParams(params) }).then(response => {
        console.log({ ...response.data.data });
        console.log(getRandomuserParams(params));
        setTotalData(response.data.data);
        setLoading(false);
        setData(response.data.data);
        setPagination(params.pagination);
      });
    } catch (e) {
      console.log(e);
    };

    // reqwest({
    //   url: 'https://randomuser.me/api',
    //   method: 'get',
    //   type: 'json',
    //   data: getRandomuserParams(params),
    // }).then(data => {
    //   console.log(data.results);
    //   // this.setState({
    //   //   loading: false,
    //   //   data: data.results,
    //   //   pagination: {
    //   //     ...params.pagination,
    //   //     total: 200,
    //   //     // 200 is mock data, you should read it from server
    //   //     // total: data.totalCount,
    //   //   },
    //   // });
    //   setTotalData(data.results);
    //   setLoading(false);
    //   setData(data.results);
    //   setPagination(params.pagination);
    // });
  };




  // const suffix = (
  //   <AudioOutlined
  //     style={{
  //       fontSize: 16,
  //       color: '#1890ff',
  //     }}
  //   />
  // );

  function wildCardSearch(list, input) {
    const searchText = (item) => {
      for (let key in item) {
        if (item[key] == null) {
          continue;
        }
        if (item[key].toString().toUpperCase().indexOf(input.toString().toUpperCase()) !== -1) {
          return true;
        }
      }
    };
    list = list.filter(value => searchText(value));
    return list;
  }

  function onSearch(e) {
    const value = e.target.value;
    // const searchArray = e.currentTarget.value ? list : userListData;
    const res = wildCardSearch(totalData, value);
    setData(res)
  }


  return (
    <Card>
      <Row>
        <Col lg={18} style={{ margin: '0 auto' }}>
          {/* <Search
            placeholder="input search text"
            enterButton="Search"
            size="large"
            style={{ marginBottom: '20px' }}
            suffix={suffix}
            value={value}
            onChange={(e) => onSearch(e)}
          /> */}
          <Input size="large" value={value} placeholder="Search..."
            onChange={(e) => onSearch(e)} style={{ marginBottom: '20px' }} prefix={<SearchOutlined />} />

          <Table
            columns={columns}
            rowKey={record => record['Unnamed: 0']}
            dataSource={data}
            pagination={pagination}
            loading={loading}
            onChange={handleTableChange}
          />
        </Col>
      </Row>
    </Card>
  );
}


export default App
// import React, { Component } from 'react';
// import { BrowserRouter } from 'react-router-dom'
// import { Route, Link } from 'react-router-dom'

// import CustomersList from './CustomersList'
// import CustomerCreateUpdate from './CustomerCreateUpdate'
// import './App.css';

// const BaseLayout = () => (
//   <div className="container-fluid">
//     <nav className="navbar navbar-expand-lg navbar-light bg-light">
//       <a className="navbar-brand" href="#">Django React Demo</a>
//       <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNavAltMarkup" aria-controls="navbarNavAltMarkup" aria-expanded="false" aria-label="Toggle navigation">
//         <span className="navbar-toggler-icon"></span>
//       </button>
//       <div className="collapse navbar-collapse" id="navbarNavAltMarkup">
//         <div className="navbar-nav">
//           <a className="nav-item nav-link" href="/">CUSTOMERS</a>
//           <a className="nav-item nav-link" href="/customer">CREATE CUSTOMER</a>

//         </div>
//       </div>
//     </nav>

//     <div className="content">
//       <Route path="/" exact component={CustomersList} />
//       <Route path="/customer/:pk" component={CustomerCreateUpdate} />
//       <Route path="/customer/" exact component={CustomerCreateUpdate} />

//     </div>

//   </div>
// )

// class App extends Component {
//   render() {
//     return (
//       <BrowserRouter>
//         <BaseLayout />
//       </BrowserRouter>
//     );
//   }
// }

// export default App;
