import React, { Component } from 'react'

class Search extends Component {
  state = {
    query: '',
  }

  getInfo = (event) => {
    event.preventDefault();
    this.props.submitSearch(this.state.query)
  }

  handleInputChange = (event) => {
    this.setState({
      query: event.target.value
    })
  }

  handleSubmit = (event) => {
    event.preventDefault(); // No Loading on the page 
    this.props.submitSearch(this.state.query)
    // const data = {
    //   searchTerm:this.state.query
    // }
    // fetch('http://127.0.0.1:5000/questions/search', {
    //   method: 'POST', 
    //   headers: {
    //     'Content-Type': 'application/json',
    //   },
    //   body: JSON.stringify(data),
    // })
    // .then((response) => response.json())
    // .then((data) => {
    //   console.log('Success:', data);
    // })
    // .catch((error) => {
    //   console.error('Error:', error);
    // });

  }

  render() {
    return (
      <form onSubmit={this.handleSubmit}>
        <input
          placeholder="Search questions..."
          name="query"
          // ref={input => this.search = input}
          onChange={this.handleInputChange}
        />
        <input type="submit" value="Submit" className="button"/>
      </form>
    )
  }
}

export default Search
